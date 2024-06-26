import {
  ParticipantsAudio,
  SfuModels,
  useCallStateHooks,
} from "@stream-io/video-react-sdk";
import { Participant } from "./Participant";
import styles from "./styles/ParticipantsPanel.module.css";

export const ParticipantsPanel = () => {
  const hasAudio = (p) => p.publishedTracks.includes(SfuModels.TrackType.AUDIO);

  const { useParticipants } = useCallStateHooks();

  const participants = useParticipants();
  const speakers = participants.filter((p) => hasAudio(p));
  const listeners = participants.filter((p) => !hasAudio(p));

  return (
    <div className={styles["participants-panel"]}>
      <div className={styles["participants-section"]}>
        <p className={styles["participants-header"]}>
          Speakers ({speakers.length})
        </p>
        <ParticipantsAudio participants={speakers} />
        <div className={styles["participants-body"]}>
          {speakers.length > 0 ? (
            speakers.map((p) => (
              <Participant participant={p} key={p.sessionId} />
            ))
          ) : (
            <p className={styles["notification-bar"]}>
              No speakers at the moment.
            </p>
          )}
        </div>
      </div>
      <div className={styles["participants-section"]}>
        <p className={styles["participants-header"]}>
          Listeners ({listeners.length})
        </p>
        <div className={styles["participants-body"]}>
          {listeners.length > 0 ? (
            listeners.map((p) => (
              <Participant participant={p} key={p.sessionId} />
            ))
          ) : (
            <p className={styles["notification-bar"]}>
              No listeners at the moment.
            </p>
          )}
        </div>
      </div>
    </div>
  );
};
