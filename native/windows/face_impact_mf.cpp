// Media Foundation bridge for one exact video-device symbolic link.
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <mfapi.h>
#include <mferror.h>
#include <mfidl.h>
#include <mfreadwrite.h>
#include <dshow.h>
#include <wrl/client.h>
#include <cwchar>
#include <memory>
#include <new>
#include <cstring>
#include <utility>
#include <string>

using Microsoft::WRL::ComPtr;
#define OFI_API extern "C" __declspec(dllexport)
#define CHECK(call) do { HRESULT status = (call); if (FAILED(status)) return status; } while (0)

struct ComScope {
    HRESULT result = CoInitializeEx(nullptr, COINIT_MULTITHREADED);
    ~ComScope() { if (SUCCEEDED(result)) CoUninitialize(); }
};

class ReaderCallback final : public IMFSourceReaderCallback {
    LONG refs = 1;
public:
    HANDLE event = CreateEventW(nullptr, FALSE, FALSE, nullptr);
    HRESULT status = S_OK;
    DWORD flags = 0;
    LONGLONG callback_time = -1;
    LARGE_INTEGER callback_qpc{};
    ComPtr<IMFSample> sample;

    ~ReaderCallback() { if (event) CloseHandle(event); }
    STDMETHODIMP QueryInterface(REFIID iid, void** out) override {
        if (iid != __uuidof(IUnknown) && iid != __uuidof(IMFSourceReaderCallback)) {
            *out = nullptr;
            return E_NOINTERFACE;
        }
        *out = static_cast<IMFSourceReaderCallback*>(this);
        AddRef();
        return S_OK;
    }
    STDMETHODIMP_(ULONG) AddRef() override { return InterlockedIncrement(&refs); }
    STDMETHODIMP_(ULONG) Release() override {
        ULONG remaining = InterlockedDecrement(&refs);
        if (!remaining) delete this;
        return remaining;
    }
    STDMETHODIMP OnReadSample(HRESULT result, DWORD, DWORD stream_flags, LONGLONG timestamp, IMFSample* frame) override {
        QueryPerformanceCounter(&callback_qpc);
        status = result;
        flags = stream_flags;
        callback_time = frame ? timestamp : -1;
        sample = frame;
        SetEvent(event);
        return S_OK;
    }
    STDMETHODIMP OnEvent(DWORD, IMFMediaEvent*) override { return S_OK; }
    STDMETHODIMP OnFlush(DWORD) override { return S_OK; }
};

struct Session {
    ComPtr<IMFMediaSource> source;
    ComPtr<IMFSourceReader> reader;
    ComPtr<ReaderCallback> callback;
    bool started = false;
    LARGE_INTEGER qpc_frequency{};
    std::wstring identity;
    ~Session() {
        reader.Reset();
        if (source) source->Shutdown();
        source.Reset();
        callback.Reset();
        if (started) MFShutdown();
    }
};

struct TaskMem {
    void operator()(wchar_t* p) const { CoTaskMemFree(p); }
};
struct Devices {
    IMFActivate** items = nullptr;
    UINT32 count = 0;
    ~Devices() {
        for (UINT32 i = 0; i < count; ++i) items[i]->Release();
        CoTaskMemFree(items);
    }
};

static HRESULT start(Session& session) {
    CHECK(MFStartup(MF_VERSION));
    session.started = true;
    return S_OK;
}

static HRESULT enumerate(Devices& devices) {
    ComPtr<IMFAttributes> attrs;
    CHECK(MFCreateAttributes(&attrs, 1));
    CHECK(attrs->SetGUID(MF_DEVSOURCE_ATTRIBUTE_SOURCE_TYPE, MF_DEVSOURCE_ATTRIBUTE_SOURCE_TYPE_VIDCAP_GUID));
    return MFEnumDeviceSources(attrs.Get(), &devices.items, &devices.count);
}

static HRESULT attribute(IMFActivate* entry, REFGUID key, std::unique_ptr<wchar_t, TaskMem>& value) {
    wchar_t* raw = nullptr;
    UINT32 length = 0;
    HRESULT hr = entry->GetAllocatedString(key, &raw, &length);
    value.reset(raw);
    return hr;
}

using DeviceCallback = void (*)(const wchar_t*, const wchar_t*);
OFI_API HRESULT ofi_scan(DeviceCallback callback) {
    ComScope com;
    CHECK(com.result);
    Session session;
    CHECK(start(session));
    Devices devices;
    CHECK(enumerate(devices));
    for (UINT32 i = 0; i < devices.count; ++i) {
        std::unique_ptr<wchar_t, TaskMem> link, name;
        if (SUCCEEDED(attribute(devices.items[i], MF_DEVSOURCE_ATTRIBUTE_SOURCE_TYPE_VIDCAP_SYMBOLIC_LINK, link))) {
            attribute(devices.items[i], MF_DEVSOURCE_ATTRIBUTE_FRIENDLY_NAME, name);
            callback(link.get(), name ? name.get() : link.get());
        }
    }
    return S_OK;
}

static HRESULT connect(Session& session, const wchar_t* requested) {
    CHECK(start(session));
    Devices devices;
    CHECK(enumerate(devices));
    IMFActivate* selected = nullptr;
    for (UINT32 i = 0; i < devices.count; ++i) {
        std::unique_ptr<wchar_t, TaskMem> link;
        if (SUCCEEDED(attribute(devices.items[i], MF_DEVSOURCE_ATTRIBUTE_SOURCE_TYPE_VIDCAP_SYMBOLIC_LINK, link))
            && _wcsicmp(requested, link.get()) == 0) {
            if (selected) return HRESULT_FROM_WIN32(ERROR_DUP_NAME);
            selected = devices.items[i];
            session.identity.assign(link.get());
        }
    }
    if (!selected) return HRESULT_FROM_WIN32(ERROR_NOT_FOUND);
    // Activate the exact matched device entry, without using an enumeration index.
    CHECK(selected->ActivateObject(IID_PPV_ARGS(&session.source)));
    ComPtr<IMFAttributes> attrs;
    CHECK(MFCreateAttributes(&attrs, 1));
    CHECK(attrs->SetUINT32(MF_READWRITE_DISABLE_CONVERTERS, TRUE));
    session.callback.Attach(new (std::nothrow) ReaderCallback);
    if (!session.callback) return E_OUTOFMEMORY;
    if (!session.callback->event) return HRESULT_FROM_WIN32(GetLastError());
    CHECK(attrs->SetUnknown(MF_SOURCE_READER_ASYNC_CALLBACK, session.callback.Get()));
    CHECK(MFCreateSourceReaderFromMediaSource(session.source.Get(), attrs.Get(), &session.reader));
    CHECK(session.reader->SetStreamSelection(MF_SOURCE_READER_ALL_STREAMS, FALSE));
    return session.reader->SetStreamSelection(MF_SOURCE_READER_FIRST_VIDEO_STREAM, TRUE);
}

struct Mode { UINT32 width, height, numerator, denominator, format; };
static bool read_mode(IMFMediaType* type, Mode& mode) {
    GUID subtype;
    if (FAILED(type->GetGUID(MF_MT_SUBTYPE, &subtype))) return false;
    mode.format = subtype == MFVideoFormat_YUY2 ? 1 : subtype == MFVideoFormat_NV12 ? 2 :
                  subtype == MFVideoFormat_MJPG ? 3 : 0;
    return mode.format && SUCCEEDED(MFGetAttributeSize(type, MF_MT_FRAME_SIZE, &mode.width, &mode.height))
        && SUCCEEDED(MFGetAttributeRatio(type, MF_MT_FRAME_RATE, &mode.numerator, &mode.denominator))
        && mode.width && mode.height && mode.numerator && mode.denominator;
}
using ModeCallback = void (*)(const Mode*);
OFI_API HRESULT ofi_modes(const wchar_t* link, ModeCallback callback) {
    ComScope com;
    CHECK(com.result);
    Session session;
    CHECK(connect(session, link));
    for (DWORD i = 0; ; ++i) {
        ComPtr<IMFMediaType> type;
        HRESULT hr = session.reader->GetNativeMediaType(MF_SOURCE_READER_FIRST_VIDEO_STREAM, i, &type);
        if (hr == MF_E_NO_MORE_TYPES) return S_OK;
        CHECK(hr);
        Mode mode{};
        if (read_mode(type.Get(), mode)) callback(&mode);
    }
}
OFI_API HRESULT ofi_open(const wchar_t* link, const Mode* wanted, Session** output) {
    ComScope com;
    CHECK(com.result);
    std::unique_ptr<Session> session(new (std::nothrow) Session);
    if (!session) return E_OUTOFMEMORY;
    CHECK(connect(*session, link));
    QueryPerformanceFrequency(&session->qpc_frequency);
    for (DWORD i = 0; ; ++i) {
        ComPtr<IMFMediaType> type;
        HRESULT hr = session->reader->GetNativeMediaType(MF_SOURCE_READER_FIRST_VIDEO_STREAM, i, &type);
        if (hr == MF_E_NO_MORE_TYPES) return MF_E_INVALIDMEDIATYPE;
        CHECK(hr);
        Mode mode{};
        if (!read_mode(type.Get(), mode) || mode.width != wanted->width || mode.height != wanted->height ||
            mode.numerator != wanted->numerator || mode.denominator != wanted->denominator || mode.format != wanted->format)
            continue;
        CHECK(session->reader->SetCurrentMediaType(MF_SOURCE_READER_FIRST_VIDEO_STREAM, nullptr, type.Get()));
        ComPtr<IMFMediaType> negotiated;
        CHECK(session->reader->GetCurrentMediaType(MF_SOURCE_READER_FIRST_VIDEO_STREAM, &negotiated));
        Mode actual{};
        if (!read_mode(negotiated.Get(), actual) || actual.width != mode.width ||
            actual.height != mode.height || actual.numerator != mode.numerator ||
            actual.denominator != mode.denominator || actual.format != mode.format)
            return MF_E_INVALIDMEDIATYPE;
        *output = session.release();
        return S_OK;
    }
}

OFI_API const wchar_t* ofi_identity(Session* session) { return session->identity.c_str(); }

struct FrameInfo {
    LONGLONG time_100ns, duration_100ns, callback_time_100ns;
    DWORD bytes, flags;
    UINT32 discontinuity;
    LONGLONG callback_qpc_ticks, qpc_frequency_hz, readout_qpc_ticks;
};
OFI_API HRESULT ofi_read(Session* session, BYTE* output, DWORD capacity, FrameInfo* info) {
    ComScope com;
    CHECK(com.result);
    auto* cb = session->callback.Get();
    CHECK(session->reader->ReadSample(MF_SOURCE_READER_FIRST_VIDEO_STREAM, 0, nullptr, nullptr, nullptr, nullptr));
    if (WaitForSingleObject(cb->event, 1500) != WAIT_OBJECT_0)
        return HRESULT_FROM_WIN32(ERROR_TIMEOUT);
    CHECK(cb->status);
    DWORD flags = cb->flags;
    ComPtr<IMFSample> sample = std::move(cb->sample);
    if (flags & (MF_SOURCE_READERF_ERROR | MF_SOURCE_READERF_ENDOFSTREAM |
                 MF_SOURCE_READERF_CURRENTMEDIATYPECHANGED | MF_SOURCE_READERF_NATIVEMEDIATYPECHANGED))
        return MF_E_INVALIDSTREAMNUMBER;
    if (!sample) return S_FALSE;
    info->flags = flags;
    info->callback_qpc_ticks = cb->callback_qpc.QuadPart;
    info->qpc_frequency_hz = session->qpc_frequency.QuadPart;
    info->callback_time_100ns = cb->callback_time;
    if (FAILED(sample->GetSampleTime(&info->time_100ns))) info->time_100ns = -1;
    if (FAILED(sample->GetSampleDuration(&info->duration_100ns))) info->duration_100ns = -1;
    if (FAILED(sample->GetUINT32(MFSampleExtension_Discontinuity, &info->discontinuity)))
        info->discontinuity = 0;
    ComPtr<IMFMediaBuffer> buffer;
    CHECK(sample->ConvertToContiguousBuffer(&buffer));
    ComPtr<IMF2DBuffer> two_d;
    if (SUCCEEDED(buffer.As(&two_d))) {
        CHECK(two_d->GetContiguousLength(&info->bytes));
        if (info->bytes > capacity) return HRESULT_FROM_WIN32(ERROR_INSUFFICIENT_BUFFER);
        CHECK(two_d->ContiguousCopyTo(output, info->bytes));
        LARGE_INTEGER readout{};
        QueryPerformanceCounter(&readout);
        info->readout_qpc_ticks = readout.QuadPart;
        return S_OK;
    }
    BYTE* bytes = nullptr;
    CHECK(buffer->Lock(&bytes, nullptr, &info->bytes));
    HRESULT result = S_OK;
    if (info->bytes > capacity) result = HRESULT_FROM_WIN32(ERROR_INSUFFICIENT_BUFFER);
    else if (info->bytes) std::memcpy(output, bytes, info->bytes);
    buffer->Unlock();
    LARGE_INTEGER readout{};
    QueryPerformanceCounter(&readout);
    info->readout_qpc_ticks = readout.QuadPart;
    return result;
}

OFI_API HRESULT ofi_control(Session* session, UINT32 control, BOOL set, LONG* value, LONG* flags) {
    ComScope com;
    CHECK(com.result);
    if (control == 15) {
        ComPtr<IAMCameraControl> camera;
        CHECK(session->source.As(&camera));
        return set ? camera->Set(CameraControl_Exposure, *value, *flags)
                   : camera->Get(CameraControl_Exposure, value, flags);
    }
    if (control == 14) {
        ComPtr<IAMVideoProcAmp> camera;
        CHECK(session->source.As(&camera));
        return set ? camera->Set(VideoProcAmp_Gain, *value, *flags)
                   : camera->Get(VideoProcAmp_Gain, value, flags);
    }
    return E_INVALIDARG;
}
OFI_API HRESULT ofi_control_range(Session* session, UINT32 control, LONG* minimum, LONG* maximum,
                                  LONG* step, LONG* default_value, LONG* flags) {
    ComScope com;
    CHECK(com.result);
    if (control == 15) {
        ComPtr<IAMCameraControl> camera;
        CHECK(session->source.As(&camera));
        return camera->GetRange(CameraControl_Exposure, minimum, maximum, step, default_value, flags);
    }
    if (control == 14) {
        ComPtr<IAMVideoProcAmp> camera;
        CHECK(session->source.As(&camera));
        return camera->GetRange(VideoProcAmp_Gain, minimum, maximum, step, default_value, flags);
    }
    return E_INVALIDARG;
}
OFI_API void ofi_close(Session* session) {
    ComScope com;
    delete session;
}
