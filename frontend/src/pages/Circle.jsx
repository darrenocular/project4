import React, { useState, useContext, useEffect } from "react";
import { Link, useParams } from "react-router-dom";
import useFetch from "../hooks/useFetch";
import AppContext from "../context/AppContext";
import styles from "./styles/Circle.module.css";
import Button from "../components/utils/Button";

const Circle = () => {
  const appContext = useContext(AppContext);
  const fetchData = useFetch();
  const { circleId } = useParams();
  const [circle, setCircle] = useState({ is_live: true });
  const [tags, setTags] = useState([]);
  const [isRegistered, setIsRegistered] = useState(false);
  const [registeredUsers, setRegisteredUsers] = useState([]);

  const getCircle = async () => {
    try {
      const res = await fetchData(
        "/circles/get",
        "POST",
        {
          circle_id: circleId,
        },
        appContext.accessToken
      );

      if (res.ok) {
        setCircle(res.data);
      } else {
        throw new Error(
          typeof res.msg === "object" ? JSON.stringify(res.msg) : res.msg
        );
      }
    } catch (error) {
      console.error(error.message);
    }
  };

  const getTags = async () => {
    try {
      const res = await fetchData(
        "/circles/tags",
        "POST",
        {
          circle_id: circleId,
        },
        appContext.accessToken
      );

      if (res.ok) {
        setTags(res.data);
      } else {
        throw new Error(
          typeof res.msg === "object" ? JSON.stringify(res.msg) : res.msg
        );
      }
    } catch (error) {
      console.error(error.message);
    }
  };

  const getRegisteredUsers = async () => {
    try {
      const res = await fetchData(
        "/circles/registrations",
        "POST",
        {
          circle_id: circleId,
        },
        appContext.accessToken
      );

      if (res.ok) {
        setRegisteredUsers(res.data);
      } else {
        throw new Error(
          typeof res.msg === "object" ? JSON.stringify(res.msg) : res.msg
        );
      }
    } catch (error) {
      console.error(error.message);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    try {
      if (!isRegistered) {
        const res = await fetchData(
          "/circles/register",
          "PUT",
          {
            circle_id: circleId,
          },
          appContext.accessToken
        );

        if (res.ok) {
          setIsRegistered(true);
          console.log(res.msg);
        } else {
          throw new Error(
            typeof res.msg === "object" ? JSON.stringify(res.msg) : res.msg
          );
        }
      } else {
        const res = await fetchData(
          "/circles/register",
          "DELETE",
          {
            circle_id: circleId,
          },
          appContext.accessToken
        );

        if (res.ok) {
          setIsRegistered(false);
          console.log(res.msg);
        } else {
          throw new Error(
            typeof res.msg === "object" ? JSON.stringify(res.msg) : res.msg
          );
        }
      }
    } catch (error) {
      console.error(error.message);
    }
  };

  // Get circle details when page loads
  useEffect(() => {
    getCircle();
    getTags();
    getRegisteredUsers();
  }, []);

  // Check if current user is registered
  useEffect(() => {
    for (const user of registeredUsers) {
      if (user.id === appContext.loggedInUser.id) {
        setIsRegistered(true);
      } else {
        setIsRegistered(false);
      }
    }
  }, [registeredUsers]);

  return (
    <div className={styles["circle-page"]}>
      <div className={styles["circle-info"]}>
        <div className={styles["circle-header"]}>
          <div className={styles["status-bar"]}>
            {circle["is_live"] ? (
              <>
                <img
                  src="https://upload.wikimedia.org/wikipedia/commons/8/8b/Red_Circle_full.png"
                  alt="live"
                ></img>
                <span className={styles["live"]}>Live</span>
              </>
            ) : (
              <>
                <img
                  src="https://upload.wikimedia.org/wikipedia/commons/thumb/a/a8/Circle_Davys-Grey_Solid.svg/2048px-Circle_Davys-Grey_Solid.svg.png"
                  alt="upcoming"
                ></img>
                <span className={styles["upcoming"]}>Not live yet</span>
              </>
            )}
          </div>
          <p className={styles["title"]}>{circle.title}</p>
        </div>
        <div className={styles["info-panel"]}>
          <div className={styles["tags-container"]}>
            {tags.map((tag, idx) => (
              <div key={idx}>{tag}</div>
            ))}
          </div>
          <Link
            to={`/profile/${circle.host_id}`}
            className={styles["host-container"]}
          >
            <img
              className={styles["host-img"]}
              src={`https://getstream.io/random_svg/?name=user`}
            ></img>
            <span className={styles["username"]}>@{circle.username}</span>
            <span className={styles["host-tag"]}>Host</span>
          </Link>
          {!circle["is_live"] && (
            <p className={styles["start-date"]}>
              <b>Scheduled for:</b> {circle.start_date}
            </p>
          )}
          <p>
            <b>Capacity:</b> {circle.participants_limit}
          </p>
          <p>
            <b>Sign ups:</b> XX
          </p>
          <p>
            <b>Description: </b>
            {circle.description}
          </p>
        </div>
        <div className={styles["circle-footer"]}></div>
      </div>
      <div className={styles["circle-actions"]}>
        {!circle["is_live"] &&
          circle["host_id"] !== appContext.loggedInUser.id && (
            <>
              <Button type="button" className="interested-btn">
                I'm interested!
              </Button>
              <Button
                type="button"
                className={
                  isRegistered ? "register-btn-active" : "register-btn"
                }
                onClick={handleRegister}
              >
                {isRegistered ? "I'm going!" : "Sign me up!"}
              </Button>
            </>
          )}
        {circle["host_id"] === appContext.loggedInUser.id && (
          <Button
            type="button"
            className={circle["is_live"] ? "live-btn-active" : "live-btn"}
          >
            {circle["is_live"] ? "Live now" : "Go live"}
          </Button>
        )}
      </div>
    </div>
  );
};

export default Circle;