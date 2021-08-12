import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';
import {usePromiseTracker} from 'react-promise-tracker'
import {Loader} from 'react-loader-spinner';
import Footer from './Footer/Footer'
import { FormText } from 'react-bootstrap';
import {BrowserRouter as Router} from 'react-router-dom'


ReactDOM.render(
  <React.StrictMode>
    {/* <div> */}
      <App />
      {/* <LoadingIndicator /> */}
    {/* <div> */}
  </React.StrictMode>,
  document.getElementById('root')
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();