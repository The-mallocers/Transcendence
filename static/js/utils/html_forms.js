
const Fetch_Error =  `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Server Error</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      text-align: center;
      padding: 50px;
      background-color: #f2f2f2;
      color: #333;
    }
    .error-container {
      display: inline-block;
      padding: 20px;
      border: 1px solid #ccc;
      background-color: #fff;
      border-radius: 10px;
      box-shadow: 0 0 10px rgba(0,0,0,0.1);
    }
  </style>
</head>
<body>
  <div class="error-container">
    <h1>Oops!</h1>
    <p>There was an error while fetching your data.</p>
    <p>This might be on us, but try to check your internet connection and try again.</p>
  </div>
</body>
</html>
`;

const Internal_Server_Error =  `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Server Error</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      text-align: center;
      padding: 50px;
      background-color: #f2f2f2;
      color: #333;
    }
    .error-container {
      display: inline-block;
      padding: 20px;
      border: 1px solid #ccc;
      background-color: #fff;
      border-radius: 10px;
      box-shadow: 0 0 10px rgba(0,0,0,0.1);
    }
  </style>
</head>
<body>
  <div class="error-container">
    <h1>Oops!</h1>
    <p>Internal Server error</p>
  </div>
</body>
</html>
`;
export {Fetch_Error}
export {Internal_Server_Error}