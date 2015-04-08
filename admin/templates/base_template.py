base_template = """
<!DOCTYPE html>
<html>
<head>
    <meta content="width:device-width">
    <meta content="text/html; charset=utf-8" http-equiv="Content-Type">
    <style type="text/css">
        th {{
                border: 1px solid black;
            }}

        .table {{
            width:75%;
            border: 1px solid black;
            border-collapse: collapse;
        }}

        .content {{
            border:2px solid #f0ad4e;
            border-radius:5px;
            padding: 2% 5%;
            background-color:#F9ECD8;
        }}

        .container {{
             background-color:white;
             width:100%;
             height:100%;
        }}

        .logo {{
            padding-top:16px;
            width:7%;
            float:unset;
        }}

        .imgclass {{
            padding-left:10%;
            padding-right:10%;
        }}

        .impdiv {{
            padding-left:10%;
            padding-right:10%;
            padding-top:2%;
        }}

        .contact {{
             padding-right:1%
        }}

    </style>
</head>
<body>
    <div class='container'>
        <div class="imgclass">
            <span>
                <img class="logo" src="https://sevame.in/images/ignore/Shape.png">
            <span>
        </div>
        <div class="impdiv">
            <div class="content">

                {template_content}
            </div>
            <div class="footerdiv" style="padding-top:2%">
                <div style="float:left; width:30%">
                    <span><a href="file:///Users/krishna/Downloads/facebook-48.jpg"><img src="https://sevame.in/images/ignore/facebook.png"></a></span>
                    <span><a href="file:///Users/krishna/Downloads/twitter-48.jpg"><img src= "https://sevame.in/images/ignore/twitter.png"></a></span>
                </div>
                <div style="float:right;  width:70%; color:#f0ad4e; text-align: right; padding-top:8px">
                    <span>
                            <span class="contact">Phone: +91-9901971321</span>
                            <span class="contact">Email: <a href="mailto:contact@sevame.in" style="color:#f0ad4e">contact@sevame.in</a></span>
                    </span>
                </div>
            </div>

        </div>
    </div>

</body>
</html>
"""