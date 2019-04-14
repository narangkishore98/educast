<?php 
session_start();
if(isset($_SESSION['adminmail']))
{
    header("Location:dashboard.php");
}
if(isset($_POST['username']) && isset($_POST['password']))
{
    
        $username=$_POST['username'];
        $password=$_POST['password'];
        if(strcmp($username,"shivohamapp")==0)
        {
            if(strcmp($password,"narangweb")==0)
            {
                $_SESSION['adminmail']='shivoham';
                header("Location:dashboard.php");
            }
            else
            {
                header("Location:index.php?login=False");
            }
        }
        else
        {
            header("Location:index.php?login=False");
        }
        
    
}
?>
<html>
    <head>
        <title>Admin Login - Shivoham Sewa Mandal</title>
        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
        <script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.9/umd/popper.min.js" integrity="sha384-ApNbgh9B+Y1QKtv3Rn7W3mgPxhU9K/ScQsAP7hUibX39j7fakFPskvXusvfa0b4Q" crossorigin="anonymous"></script>
        <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>
        <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.0.13/css/all.css" integrity="sha384-DNOHZ68U8hZfKXOrtjWvjxusGo9WQnrNx2sqG0tfsghAvtVlRW3tvkXWZh58N9jp" crossorigin="anonymous">
    </head>
    <body style="font-family:garamond; ">
        <div class="container-fluid">
        <div class="row bg-danger">
            <div class=col-md-12>
                <h1 class="text-center text-light">Shivoham Sewa Mandal - Admin</h1>
                
            </div>
        </div>
        <div class="row m-5 ">
            <div class="col-md-3"></div>
            <div class="col-md-6 p-5 bg-dark text-light">
                <h2>Login Here.</h2>
                <p>Login with the credentials provided to you<br/>
                Shivoham Sewa Mandal -  Admin privileges</p>
                <hr/>
                <form method="POST" action="<?php $_POST_SELF ?>">
                    <input type="text" name="username" placeholder="Username" class="form-control my-2"/>
                    <input type="password" name="password" placeholder="Password" class="form-control my-2"/>
                    <button type="submit"  class="btn btn-control btn-light form-control "><i class="fas fa-key"></i> Login Now</button>
                    
                    <?php
                        
                        if(isset($_GET['login']))
                        {
                            if(strcmp($_GET['login'],"False")==0)
                            {
                                ?>
                    <div class="alert alert-danger my-3" role="alert">
                        Incorrect Username or Password
                    </div>

                                <?php
                            }
                        }
                     ?>
                </form>
            </div>
            <div class="col-md-3"></div>
        </div>

        <div class="row bg-light p-1" style="position: fixed;
    left: 0;
    bottom: 0;
    width: 100%;
    background-color: red;
    color: white;
    text-align: center;">
            <div class="col-md-12">
                <h6 class="text-center text-dark">Website made with <i class="fas fa-heart text-danger"></i> by <a href="http://bikloo.co.nf" style="text-decoration:none;" class="text-dark">Bikloo </a> in India</h6>
            </div>
        </div>
        </div>
    </body>
</html>