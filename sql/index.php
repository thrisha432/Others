<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login Page</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
        }
        .container {
            max-width: 400px;
            margin: 50px auto;
            padding: 20px;
            background-color: #fff;
            border-radius: 5px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        h2 {
            text-align: center;
            margin-bottom: 20px;
        }
        input[type="text"],
        input[type="password"],
        input[type="submit"] {
            width: 100%;
            padding: 10px;
            margin-bottom: 15px;
            border: 1px solid #ccc;
            border-radius: 4px;
            box-sizing: border-box;
        }
        input[type="submit"] {
            background-color: #4caf50;
            color: white;
            cursor: pointer;
        }
        input[type="submit"]:hover {
            background-color: #45a049;
        }
        .error {
            color: red;
            font-size: 14px;
            margin-bottom: 10px;
        }
        .success {
            color: green;
            font-size: 14px;
            margin-bottom: 10px;
        }
    </style>
</head>
<body>

<div class="container">
    <p><b>Level-2: Authentication Bypass</b></p>
    <h2>Login</h2>
    <form method="post">
        <input type="text" name="username" placeholder="Username" required><br>
        <input type="password" name="password" placeholder="Password"><br>
        <input type="submit" value="Login">
    </form>
    <?php
    if ($_SERVER["REQUEST_METHOD"] == "POST") {
        // Database configuration
        $servername = "localhost";
        $username = "root";
        $password = "pass123"; // Replace with your MySQL root password
        $dbname = "sql_injection_demo";

        // Create connection
        $conn = new mysqli($servername, $username, $password, $dbname);

        // Check connection
        if ($conn->connect_error) {
            die("Connection failed: " . $conn->connect_error);
        }

        // Retrieve username and password from POST data
        $input_username = $_POST['username'];
        $input_password = $_POST['password'];

        // Check if the username contains SQL comments
       if (strpos($input_username, "=") !== false || strpos($input_password, "=") !== false || strpos($input_username, "--") !== false || strpos($input_password, "--") !== false) {
           // SQL injection detected, bypass password check
           echo "<p class='error'>SQL injection detected!!!</p>";
           exit();
       } else{
            // SQL query to fetch user details
            $sql = "SELECT * FROM users WHERE username='$input_username' and password ='$input_password'";
            $result = $conn->query($sql);
          if ($result->num_rows > 0) {
                // Username exists, check password
                $row = $result->fetch_assoc();
                if ($row['password'] == $input_password) {
                    // Password matches, redirect to welcome page
                    header("Location: welcome.php");
                    exit();
                } else {
                    // Password does not match
                    echo "<p class='error'>Invalid password.</p>";
                }
            } else {
                // Username does not exist
                echo "<p class='error'>Invalid username.</p>";
            }
        }

        $conn->close();
    }
    ?>
</div>

</body>
</html>
