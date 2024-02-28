/*
 * ATTENTION: The "eval" devtool has been used (maybe by default in mode: "development").
 * This devtool is neither made for production nor for readable output files.
 * It uses "eval()" calls to create a separate source file in the browser devtools.
 * If you are trying to read the output file, select a different devtool (https://webpack.js.org/configuration/devtool/)
 * or disable the default devtool with "devtool: false".
 * If you are looking for production-ready output files, see mode: "production" (https://webpack.js.org/configuration/mode/).
 */
/******/ (() => { // webpackBootstrap
/******/ 	var __webpack_modules__ = ({

/***/ "./main/static/main/js/index.js":
/*!**************************************!*\
  !*** ./main/static/main/js/index.js ***!
  \**************************************/
/***/ (() => {

eval("async function subscribe_toggle(action) {\n  try {\n    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;\n    const url = `subscribe_toggle/${action}/`;\n    const response = await fetch(url, {\n      method: 'POST',\n      headers: {\n        'Content-Type': 'application/json',\n        'X-CSRFToken': csrftoken\n      }\n    });\n    if (!response.ok) {\n      console.error('Network response was not ok');\n      return;\n    }\n    const data = await response.json();\n    updateButton(data);\n    updateSubscribersCount(data.subscribers_count);\n  } catch (error) {\n    console.error('Error:', error.message);\n  }\n}\nfunction updateButton(data) {\n  const button = document.getElementById('subscribeButton');\n  button.innerText = data.is_subscribed ? 'Subscribe' : 'Unsubscribe';\n  button.onclick = () => subscribe_toggle(data.is_subscribed ? 'subscribe' : 'unsubscribe');\n}\nfunction updateSubscribersCount(count) {\n  const subscribersCountElement = document.getElementById('subscribersCount');\n  if (subscribersCountElement) {\n    subscribersCountElement.innerText = `${count} subscribers`;\n  }\n}\ndocument.querySelectorAll('.like-button, .dislike-button').forEach(button => {\n  button.addEventListener('click', async function () {\n    const postId = this.getAttribute('data-post-id');\n    const action = this.getAttribute('data-action');\n    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;\n    const toggleLikeUrl = `/user/toggle_like/${postId}/${action}/`;\n    try {\n      const response = await fetch(toggleLikeUrl, {\n        method: 'POST',\n        headers: {\n          'Content-Type': 'application/json',\n          'X-CSRFToken': csrftoken\n        }\n      });\n      if (!response.ok) {\n        console.error('Network response was not ok');\n        return;\n      }\n      const data = await response.json();\n      updateLikesAndDislikes(data);\n    } catch (error) {\n      console.error('Error:', error.message);\n    }\n  });\n});\nfunction updateLikesAndDislikes(data) {\n  document.getElementById(`like-count-${data.post_id}`).innerText = data.likes;\n  document.getElementById(`dislike-count-${data.post_id}`).innerText = data.dislikes;\n}\n\n//# sourceURL=webpack://djangogramm/./main/static/main/js/index.js?");

/***/ })

/******/ 	});
/************************************************************************/
/******/ 	
/******/ 	// startup
/******/ 	// Load entry module and return exports
/******/ 	// This entry module can't be inlined because the eval devtool is used.
/******/ 	var __webpack_exports__ = {};
/******/ 	__webpack_modules__["./main/static/main/js/index.js"]();
/******/ 	
/******/ })()
;