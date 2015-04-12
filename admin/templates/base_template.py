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
            width:75%;border: 1px solid black;border-collapse: collapse;
        }}

        .content {{
            border:2px solid #f0ad4e;border-radius:5px;padding: 2% 5%;background-color:#F9ECD8;
        }}

        .container {{
             background-color:white;width:100%;height:100%;
        }}

        .logo {{
            padding-top:16px;width:7%;float:unset;
        }}

        .imgclass {{
            padding-left:10%;padding-right:10%;
        }}

        .impdiv {{
            padding-left:10%;padding-right:10%;padding-top:2%;
        }}

        .contact {{
             padding-right:1%
        }}

    </style>
</head>
<body>
    <div class='container' style="background-color:white;width:100%;height:100%;">
        <div class="imgclass" style="padding-left:10%;padding-right:10%;">
            <span>
                <img class="logo" style="padding-top:16px;width:7%;float:unset;" src="https://sevame.in/images/ignore/Shape.png">
            <span>
        </div>
        <div class="impdiv" style="padding-left:10%;padding-right:10%;padding-top:2%;">
            <div class="content" style="border:2px solid #f0ad4e;border-radius:5px;padding: 2% 5%;background-color:#F9ECD8;">

                {template_content}
            </div>
            <div class="footerdiv" style="padding-top:2%">
                <div style="float:left; width:30%">
                    <span><a href="https://sevame.in/images/ignore/facebook.jpg"><img src="https://sevame.in/images/ignore/facebook.jpg"></a></span>
                    <span><a href="https://sevame.in/images/ignore/twitter.jpg"><img src= "https://sevame.in/images/ignore/twitter.jpg"></a></span>
                </div>
                <div style="float:right;  width:70%; color:#f0ad4e; text-align: right; padding-top:8px">
                    <span>
                            <span class="contact" style="padding-right:1%">Phone: +91-8494954007</span>
                            <span class="contact" style="padding-right:1%">Email: <a href="mailto:contact@sevame.in" style="color:#f0ad4e">contact@sevame.in</a></span>
                    </span>
                </div>
            </div>

        </div>
    </div>

</body>
</html>
"""