import React from "react";
import styles from "./Button.module.css";

const Button = (props) => {
  return (
    <button
      type={props.type}
      className={`${styles.button} ${styles[props.className]}`}
      onClick={props.onClick}
      name={props.name}
    >
      {props.children}
    </button>
  );
};

export default Button;
