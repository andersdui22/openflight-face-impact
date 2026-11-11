import { useState, useEffect } from 'react';
import { useShallow } from 'zustand/react/shallow';
import { useSocket } from './hooks/useSocket';
import { useSystemStore } from './stores/useSystemStore';
import { useShotStore } from './stores/useShotStore';
import { useCameraStore } from './stores/useCameraStore';
import { useDebugStore } from './stores/useDebugStore';
import { useProfileStore } from './stores/useProfileStore';
import { useHeroMetricStore } from './stores/useHeroMetricStore';
import { useCameraReplayController } from './hooks/useCameraReplayController';
import { socketService } from './services/socketService';
import { DebugPanel } from './components/DebugPanel';
import { SyntheticFaceImpactDemo } from './components/SyntheticFaceImpactDemo';
import { FaceImpactSessionDemo, type DemoShot } from './components/FaceImpactSessionDemo';
import { FaceImpactControls } from './components/FaceImpactControls';
import { SyntheticMotionDiagnostics } from './components/SyntheticMotionDiagnostics';
import { useSyntheticMotionStore } from './stores/useSyntheticMotionStore';
import { FaceImpactCameraPreview } from './components/FaceImpactCameraPreview';
import { DisplayMode } from './components/DisplayMode';
import { SimShotBadges } from './components/SimShotBadges';
import { ShotProcessingArea } from './components/ShotProcessingArea';
import { ShutdownDialog, type ShutdownState } from './components/ShutdownDialog';
import { CameraReplayDialog } from './components/CameraReplayDialog';
import {
  CameraPanel,
  LivePanel,
  ProfileNameDialog,
  ProfilesPanel,
  ClearSessionDialog,
  SimulateBubble,
  MenuSheet,
  PanelFooter,
  PanelHeader,
  PanelAction,
  PickerOverlay,
  ShotsPanel,
  StatsPanel,
  clubSections,
  trainingImplementSections,
  type PanelView,
} from './components/panel';
import { filterShotsByProfile } from './types/shot';
import type { Profile } from './types/profile';
import { getClubName } from './data/clubs';
import { getTrainingImplementLabel } from './data/trainingImplements';
import { unlockAudioCue } from './utils/audioCue';
import { useLaunchDaddy, LaunchDaddyOverlay, LaunchDaddyBrand } from './components/LaunchDaddy';

import { useI18n } from './i18n/useI18n';
import './components/panel/panel.css';

function FaceImpactDashboard({
  onLegacy,
  onNavigate,
  shotCount,
}: {
  onLegacy: () => void;
  onNavigate: (view: PanelView) => void;
  shotCount: number;
}) {
  const syntheticMotion = useSyntheticMotionStore((state) => state.payload);
  const [demoEnabled, setDemoEnabled] = useState(false);
  const [demoShots, setDemoShots] = useState<DemoShot[]>([]);
  const demoAverage = (axis: 'x' | 'y') =>
    demoShots.length ? (demoShots.reduce((sum, shot) => sum + shot[axis], 0) / demoShots.length).toFixed(1) : '—';
  const latestDemoShot = demoShots[demoShots.length - 1];
  const panels = [
    { title: 'Side Impact', subtitle: 'Clubface contact', content: 'face' },
    { title: 'Front Impact', subtitle: 'Heel / toe · high / low', content: 'target' },
    { title: 'Top Impact', subtitle: 'Camera-derived geometry', content: 'target' },
    {
      title: 'Impact Distribution',
      subtitle: demoEnabled ? 'Simulated demo session · not measured' : 'Awaiting validated shot history',
      content: 'distribution',
    },
    { title: 'Camera Preview', subtitle: 'ELP OV9281', content: 'camera' },
    { title: 'Shot Replay', subtitle: 'Select a captured shot', content: 'replay' },
  ] as const;

  return (
    <section className="impact-workspace" aria-label="Face Impact dashboard">
      <aside className="impact-workspace__sidebar" aria-label="Session and club sidebar">
        <div className="impact-workspace__brand">
          OPENFLIGHT <span>FACE IMPACT</span>
        </div>
        <div className="impact-workspace__sidebar-title">
          SESSIONS <span>{shotCount}</span>
        </div>
        <button type="button" className="impact-workspace__session" onClick={() => onNavigate('shots')}>
          CURRENT SESSION <span>›</span>
        </button>
        <div className="impact-workspace__sidebar-title">CLUB SELECTION</div>
        <div className="impact-workspace__sidebar-note">Select a club in the existing OpenFlight interface.</div>
        <button type="button" className="impact-workspace__sidebar-link" onClick={onLegacy}>
          OPEN CLASSIC LIVE VIEW
        </button>
        <button type="button" className="impact-workspace__sidebar-link" onClick={() => onNavigate('camera')}>
          CAMERA SETTINGS
        </button>
        <button type="button" className="impact-workspace__sidebar-link" onClick={() => onNavigate('shots')}>
          SHOT HISTORY
        </button>
      </aside>
      <div className="impact-workspace__content">
        <header className="impact-workspace__topbar">
          <nav aria-label="Dashboard sections">
            <span className="impact-workspace__active">SUMMARY</span>
            <button type="button" onClick={onLegacy}>
              SWING
            </button>
            <button type="button" onClick={() => onNavigate('camera')}>
              VIDEO
            </button>
            <button type="button" onClick={() => onNavigate('shots')}>
              HISTORY
            </button>
            <button type="button" onClick={() => onNavigate('stats')}>
              STATS
            </button>
          </nav>
          <span className="impact-workspace__connection">
            FACE IMPACT · CAMERA STATUS IN PREVIEW · IMPACT DATA NOT MEASURED
          </span>
        </header>
        <div className="impact-workspace__tiles">
          {panels.map((panel) => (
            <section key={panel.title} className="impact-workspace__tile" aria-label={panel.title}>
              <div className="impact-workspace__tile-heading">{panel.title}</div>
              <div className="impact-workspace__tile-subtitle">{panel.subtitle}</div>
              {panel.content === 'face' ? (
                <div className="impact-workspace__face">
                  <SyntheticFaceImpactDemo />
                </div>
              ) : panel.content === 'distribution' ? (
                <div
                  className="impact-workspace__distribution"
                  aria-label={demoEnabled ? 'Simulated impact distribution' : 'Empty impact distribution'}
                >
                  {demoEnabled ? (
                    <>
                      <svg
                        viewBox="0 0 300 180"
                        role="img"
                        aria-label={`DEMO ONLY impact map with ${demoShots.length} simulated shots`}
                        style={{ width: '100%', maxWidth: 300 }}
                      >
                        <rect
                          x="30"
                          y="20"
                          width="240"
                          height="140"
                          rx="28"
                          fill="#243b53"
                          stroke="#8eb3cf"
                          strokeWidth="2"
                        />
                        <line x1="150" y1="20" x2="150" y2="160" stroke="#6987a1" strokeDasharray="4 4" />
                        <line x1="30" y1="90" x2="270" y2="90" stroke="#6987a1" strokeDasharray="4 4" />
                        {demoShots.map((shot) => (
                          <circle
                            key={shot.id}
                            cx={150 + shot.x * 4}
                            cy={90 - shot.y * 4}
                            r="6"
                            fill="#79c5d4"
                            stroke="#ffffff"
                            strokeWidth="1.5"
                          >
                            <title>{`SIMULATED SHOT ${shot.id}: X ${shot.x} mm, Y ${shot.y} mm`}</title>
                          </circle>
                        ))}
                        <text x="150" y="14" textAnchor="middle" fontSize="10" fill="#e5f4ff">
                          SIMULATED IMPACT MAP · DEMO ONLY
                        </text>
                      </svg>
                      <span>SIMULATED SHOTS: {demoShots.length} · NOT MEASURED</span>
                      <span>
                        DEMO AVERAGE X: {demoAverage('x')} mm · Y: {demoAverage('y')} mm
                      </span>
                    </>
                  ) : (
                    <>
                      <div className="impact-workspace__rings" />
                      <span>No measured impacts yet</span>
                    </>
                  )}
                </div>
              ) : panel.content === 'camera' ? (
                <FaceImpactCameraPreview />
              ) : panel.content === 'replay' ? (
                <div className="impact-workspace__empty">
                  <span className="impact-workspace__play">▷</span>No shot replay selected
                  <button type="button" onClick={() => onNavigate('shots')}>
                    OPEN SHOT HISTORY
                  </button>
                </div>
              ) : (
                <div className="impact-workspace__empty">
                  <span className="impact-workspace__crosshair">＋</span>Awaiting calibrated observations
                </div>
              )}
            </section>
          ))}
        </div>
        <FaceImpactSessionDemo
          enabled={demoEnabled}
          setEnabled={setDemoEnabled}
          shots={demoShots}
          setShots={setDemoShots}
        />
        <FaceImpactControls />
        <SyntheticMotionDiagnostics payload={syntheticMotion} />
        {demoEnabled && (
          <section className="impact-controls" aria-label="Simulated Face Impact metrics">
            <strong>DEMO METRICS — SIMULATED, NOT MEASURED</strong>
            <div className="impact-controls__fields">
              <span>DEMO SHOT COUNT: {demoShots.length}</span>
              <span>DEMO LAST X: {latestDemoShot?.x ?? '—'} mm</span>
              <span>DEMO LAST Y: {latestDemoShot?.y ?? '—'} mm</span>
              <span>DEMO AVERAGE X: {demoAverage('x')} mm</span>
              <span>DEMO AVERAGE Y: {demoAverage('y')} mm</span>
            </div>
          </section>
        )}
        <div className="impact-workspace__metrics" role="region" aria-label="Face Impact metrics">
          {[
            'HEEL / TOE',
            'HIGH / LOW',
            'IMPACT X',
            'IMPACT Y',
            'FACE CONTACT',
            'CAMERA FPS',
            'CALIBRATION',
            'SHOT COUNT',
          ].map((name) => (
            <div className="impact-workspace__metric" key={name}>
              <span>{name}</span>
              <strong>{name === 'SHOT COUNT' ? shotCount : '—'}</strong>
              <small>{name === 'SHOT COUNT' ? 'session shots' : 'not measured'}</small>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function AppContent() {
  const { t } = useI18n();
  const { shutdown, sleepScreen } = useSocket();
  const { connected, mockMode, debugMode, latestSimShots, serverClub } = useSystemStore(
    useShallow((state) => ({
      connected: state.connected,
      mockMode: state.mockMode,
      debugMode: state.debugMode,
      latestSimShots: state.latestSimShots,
      serverClub: state.serverClub,
    }))
  );
  const { latestShot, shots, isNewShot, shotProcessingPhase, shotVersion } = useShotStore(
    useShallow((state) => ({
      latestShot: state.latestShot,
      shots: state.shots,
      isNewShot: state.isNewShot,
      shotProcessingPhase: state.shotProcessingPhase,
      shotVersion: state.shotVersion,
    }))
  );
  const { captureSettings, captureSettingsError } = useCameraStore(
    useShallow((state) => ({
      captureSettings: state.captureSettings,
      captureSettingsError: state.captureSettingsError,
    }))
  );
  const { profiles, activeProfileId, profilesLoaded } = useProfileStore(
    useShallow((state) => ({
      profiles: state.profiles,
      activeProfileId: state.activeProfileId,
      profilesLoaded: state.loaded,
    }))
  );
  const activeProfile = profiles.find((profile) => profile.id === activeProfileId) ?? null;
  const activeProfileName = activeProfile?.name ?? '';
  const { heroMetricId, setHeroMetricId } = useHeroMetricStore(
    useShallow((state) => ({ heroMetricId: state.heroMetricId, setHeroMetricId: state.setHeroMetricId }))
  );
  const {
    debugReadings,
    debugShotLogs,
    radarConfig,
    triggerDiagnostics,
    triggerStatus,
    iwr6843Alert,
    dismissIWR6843Alert,
  } = useDebugStore(
    useShallow((state) => ({
      debugReadings: state.debugReadings,
      debugShotLogs: state.debugShotLogs,
      radarConfig: state.radarConfig,
      triggerDiagnostics: state.triggerDiagnostics,
      triggerStatus: state.triggerStatus,
      iwr6843Alert: state.iwr6843Alert,
      dismissIWR6843Alert: state.dismissIWR6843Alert,
    }))
  );

  const [currentView, setCurrentView] = useState<PanelView>('live');
  const [dashboardOpen, setDashboardOpen] = useState(false);
  const [selectedClub, setSelectedClub] = useState('driver');
  const [selectedTrainingImplement, setSelectedTrainingImplement] = useState('driver');
  const [menuOpen, setMenuOpen] = useState(false);
  const [showShutdown, setShowShutdown] = useState(false);
  const [shutdownState, setShutdownState] = useState<ShutdownState>('confirm');
  // Open on every app load so the user confirms their club before the first
  // shot; dismissing keeps the default. The /display route returns early below,
  // so this never appears in the passive TV view.
  const [pickerOpen, setPickerOpen] = useState(true);
  const [profileDialog, setProfileDialog] = useState<{ mode: 'add' | 'rename'; target: Profile | null } | null>(null);
  const [profileDialogName, setProfileDialogName] = useState('');
  const [clearSessionOpen, setClearSessionOpen] = useState(false);
  const { activeReplay, openReplay, closeReplay, reportPlaybackError } = useCameraReplayController();

  // Reflect a server-pushed club change (e.g. the club changed in the connected
  // simulator) locally without echoing back. Done during render (React's "adjust
  // state when an input changes" pattern) rather than in an effect.
  const [appliedServerClub, setAppliedServerClub] = useState<string | null>(null);
  if (serverClub && serverClub !== appliedServerClub) {
    setAppliedServerClub(serverClub);
    setSelectedClub(serverClub);
  }

  const { isLaunchDaddyMode, isExploding, triggerExplosion } = useLaunchDaddy();
  const isDisplayRoute = typeof window !== 'undefined' && window.location.pathname.replace(/\/$/, '') === '/display';
  const isSwingSpeedMode = triggerStatus.mode === 'swing-speed';
  const activeImplementLabel = isSwingSpeedMode
    ? getTrainingImplementLabel(selectedTrainingImplement)
    : getClubName(selectedClub);

  useEffect(() => {
    return socketService.onSessionCleared(() => {
      setClearSessionOpen(false);
      setCurrentView('live');
    });
  }, []);

  // Trigger explosion when a new shot is detected in Launch Daddy mode
  useEffect(() => {
    if (isNewShot && isLaunchDaddyMode) {
      triggerExplosion();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps -- shotVersion triggers the effect; isNewShot is only a guard
  }, [shotVersion, isLaunchDaddyMode, triggerExplosion]);

  useEffect(() => {
    const unlock = () => unlockAudioCue();
    window.addEventListener('pointerdown', unlock, { once: true });
    window.addEventListener('keydown', unlock, { once: true });

    return () => {
      window.removeEventListener('pointerdown', unlock);
      window.removeEventListener('keydown', unlock);
    };
  }, []);

  const handleSelectProfile = (profileId: string) => {
    socketService.setActiveProfile(profileId);
    setCurrentView('live');
  };

  const handleRemoveProfile = (profileId: string) => {
    // The server refuses to remove the active profile; don't offer it either.
    if (profileId === activeProfileId) return;
    socketService.removeProfile(profileId);
  };

  const openAddProfile = () => {
    setProfileDialog({ mode: 'add', target: null });
    setProfileDialogName('');
  };

  const openRenameProfile = (profile: Profile) => {
    setProfileDialog({ mode: 'rename', target: profile });
    setProfileDialogName(profile.name);
  };

  const closeProfileDialog = () => {
    setProfileDialog(null);
    setProfileDialogName('');
  };

  const handleConfirmProfileDialog = () => {
    const name = profileDialogName.trim();
    if (!name || !profileDialog) return;
    if (profileDialog.mode === 'add') {
      socketService.addProfile(name);
    } else if (profileDialog.target) {
      socketService.renameProfile(profileDialog.target.id, name);
    }
    closeProfileDialog();
  };

  const handlePickerSelect = (id: string) => {
    if (isSwingSpeedMode) {
      setSelectedTrainingImplement(id);
      socketService.setTrainingImplement(id);
    } else {
      setSelectedClub(id);
      socketService.setClub(id);
    }
    setPickerOpen(false);
  };

  const handleSleepScreen = async () => {
    setShowShutdown(false);

    try {
      await sleepScreen();
    } catch (error) {
      console.error('Unable to put screen to sleep:', error);
      window.alert('Unable to put screen to sleep.');
    }
  };

  const handleShutdown = async () => {
    setShutdownState('pending');
    try {
      await shutdown();
    } catch {
      setShutdownState('error');
    }
  };

  const closeShutdown = () => {
    setShowShutdown(false);
    setShutdownState('confirm');
  };

  const profileShots = filterShotsByProfile(shots, activeProfileId);
  const profileLatestShot = profileShots[profileShots.length - 1] ?? null;
  const profileIsNewShot = Boolean(
    isNewShot && latestShot && profileLatestShot && latestShot.timestamp === profileLatestShot.timestamp
  );

  if (isDisplayRoute) {
    return (
      <DisplayMode connected={connected} captureSettings={captureSettings} latestShot={latestShot} shots={shots} />
    );
  }

  const changeClubAction = (
    <PanelAction onClick={() => setPickerOpen(true)}>
      {isSwingSpeedMode ? t('app.changeImplement') : t('app.changeClub')}
    </PanelAction>
  );
  const latestReplay = profileLatestShot?.camera_replay;

  const liveHeaderActions = (
    <>
      {latestReplay ? (
        <PanelAction variant="secondary" onClick={() => openReplay(latestReplay)}>
          {t('replay.open')}
        </PanelAction>
      ) : null}
      {changeClubAction}
    </>
  );

  const addProfileAction = <PanelAction onClick={openAddProfile}>{t('menu.addProfile')}</PanelAction>;

  const clearSessionAction = (
    <PanelAction variant="danger" onClick={() => setClearSessionOpen(true)}>
      {t('app.clearSession')}
    </PanelAction>
  );

  const debugRecordAction = (
    <PanelAction variant="secondary" onClick={() => socketService.toggleDebug()}>
      {debugMode ? t('app.stopRecording') : t('app.record')}
    </PanelAction>
  );

  return (
    <div className={`panel-app ${isLaunchDaddyMode ? 'app--launch-daddy' : ''} ${isExploding ? 'app--exploding' : ''}`}>
      <LaunchDaddyOverlay />

      {iwr6843Alert && (
        <div className="iwr-alert" role="alert">
          <div>
            <strong>{t('live.tiRadarFailed')}</strong>
            <span>{t('live.tiRadarDetail', { reason: iwr6843Alert.reason })}</span>
          </div>
          <button type="button" onClick={dismissIWR6843Alert} aria-label={t('live.dismissAlert')}>
            {t('live.dismiss')}
          </button>
        </div>
      )}

      {showShutdown ? (
        <ShutdownDialog
          state={shutdownState}
          onConfirm={handleShutdown}
          onCancel={closeShutdown}
          onSleep={handleSleepScreen}
        />
      ) : null}

      {activeReplay ? (
        <CameraReplayDialog
          replay={activeReplay.replay}
          state={activeReplay.state}
          onClose={closeReplay}
          onRetry={() => openReplay(activeReplay.replay)}
          onPlaybackError={reportPlaybackError}
        />
      ) : null}

      <main className="panel-app__main">
        {currentView === 'live' && dashboardOpen && (
          <FaceImpactDashboard
            onLegacy={() => setDashboardOpen(false)}
            onNavigate={setCurrentView}
            shotCount={profileShots.length}
          />
        )}
        {currentView === 'live' && !dashboardOpen && (
          <>
            <button type="button" className="impact-workspace__return" onClick={() => setDashboardOpen(true)}>
              OPEN FACE IMPACT DASHBOARD
            </button>
            <ShotProcessingArea phase={shotProcessingPhase}>
              <LivePanel
                key={shotVersion}
                shot={profileLatestShot}
                shots={shots}
                profileId={activeProfileId}
                profileName={activeProfileName}
                clubLabel={activeImplementLabel}
                activeTrainingImplement={isSwingSpeedMode ? selectedTrainingImplement : undefined}
                selectedMetricId={heroMetricId}
                onSelectMetric={setHeroMetricId}
                isNewShot={profileIsNewShot}
                headerAction={liveHeaderActions}
              />
            </ShotProcessingArea>
            {debugMode && <SimShotBadges latestSimShots={latestSimShots} />}
          </>
        )}
        {currentView === 'profiles' && (
          <ProfilesPanel
            profiles={profiles}
            activeProfileId={activeProfileId}
            shots={shots}
            loaded={profilesLoaded}
            onSelectProfile={handleSelectProfile}
            onRenameProfile={openRenameProfile}
            onRemoveProfile={handleRemoveProfile}
            headerAction={addProfileAction}
          />
        )}
        {currentView === 'stats' && (
          <StatsPanel
            shots={shots}
            activeClub={selectedClub}
            profileId={activeProfileId}
            profileName={activeProfileName}
            headerAction={clearSessionAction}
          />
        )}
        {currentView === 'shots' && (
          <ShotsPanel
            shots={shots}
            profileId={activeProfileId}
            profileName={activeProfileName}
            clubLabel={activeImplementLabel}
            onDeleteShot={(timestamp) => socketService.deleteShot(timestamp)}
            onReplayShot={(shot) => {
              if (shot.camera_replay) openReplay(shot.camera_replay);
            }}
          />
        )}
        {currentView === 'camera' && (
          <CameraPanel
            captureSettings={captureSettings}
            captureSettingsError={captureSettingsError}
            onUpdateCaptureSettings={(settings) => socketService.setCameraCaptureSettings(settings)}
          />
        )}
        {currentView === 'debug' && (
          <div className="panel">
            <PanelHeader
              title={t('nav.debug')}
              subtitle={debugMode ? t('app.debugRecording') : t('app.debugIdle')}
              actions={debugRecordAction}
            />
            <div className="panel__body panel-app__debug">
              <SyntheticFaceImpactDemo />
              <DebugPanel
                enabled={debugMode}
                readings={debugReadings}
                shotLogs={debugShotLogs}
                radarConfig={radarConfig}
                mockMode={mockMode}
                onToggle={() => socketService.toggleDebug()}
                onUpdateConfig={(config) => socketService.setRadarConfig(config)}
                onReinitializeRadar={() => socketService.reinitializeRadar()}
                triggerDiagnostics={triggerDiagnostics}
                triggerStatus={triggerStatus}
              />
            </div>
          </div>
        )}
        {mockMode && currentView === 'live' && !dashboardOpen ? (
          <SimulateBubble
            label={isSwingSpeedMode ? t('app.simulateSwing') : t('app.simulateShot')}
            onSimulate={() => socketService.simulateShot()}
          />
        ) : null}
      </main>

      {/*
       * Overlays sit outside <main> so they cover the footer too, matching how
       * 6a draws them over the whole card.
       */}
      {menuOpen ? (
        <MenuSheet
          onClose={() => setMenuOpen(false)}
          onShutdown={() => {
            setMenuOpen(false);
            setShutdownState('confirm');
            setShowShutdown(true);
          }}
        />
      ) : null}

      {profileDialog ? (
        <ProfileNameDialog
          mode={profileDialog.mode}
          name={profileDialogName}
          onChange={setProfileDialogName}
          onConfirm={handleConfirmProfileDialog}
          onCancel={closeProfileDialog}
        />
      ) : null}

      {clearSessionOpen ? (
        <ClearSessionDialog
          profileName={activeProfileName}
          onConfirm={() => socketService.clearSession(activeProfileId)}
          onCancel={() => setClearSessionOpen(false)}
        />
      ) : null}

      {pickerOpen ? (
        <PickerOverlay
          title={isSwingSpeedMode ? t('app.selectImplement') : t('app.selectClub')}
          selectedId={isSwingSpeedMode ? selectedTrainingImplement : selectedClub}
          sections={isSwingSpeedMode ? trainingImplementSections() : clubSections()}
          onSelect={handlePickerSelect}
          onClose={() => setPickerOpen(false)}
          wide={isSwingSpeedMode}
        />
      ) : null}

      <PanelFooter
        currentView={currentView}
        onChangeView={setCurrentView}
        onOpenMenu={() => setMenuOpen((open) => !open)}
        menuOpen={menuOpen}
        shotCount={profileShots.length}
        debugRecording={debugMode}
        brand={isLaunchDaddyMode ? <LaunchDaddyBrand /> : undefined}
        onShutdown={() => {
          setShutdownState('confirm');
          setShowShutdown(true);
        }}
      />
    </div>
  );
}

function App() {
  return <AppContent />;
}

export default App;
