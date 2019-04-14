<?php 
    session_start();
    if(isset($_SESSION['adminmail'])==0)
    {
        header("Location:index.php");
    }
    if(isset($_GET['id'])==0)
    {
        header("Location:members.php");
    }
    else
    {
        $url="fdb20.biz.nf";
        $usrname="2750502_shivoham";
        $password="hypersecurity12";
        $db="2750502_shivoham";
        $conn= new mysqli($url,$usrname,$password,$db);
        $ss=$_GET['id'];
        $sql="DELETE FROM members WHERE memberid= $ss";
        $result=$conn->query($sql);
        $_SESSION['deletesuccess']='success';
        header('Location: members.php');

       
    }
?>