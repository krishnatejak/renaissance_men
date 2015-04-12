# encoding=utf8
feedback_template = """
<p>Dear {customer_name}</p>
<p>Your {service} Order No. {order_id} is completed. </p>
<p>Please rate your experience with Sevame.</p>
<form action="{rating_link}" method="GET">
    <input name="rating" type="radio" value="5"/> ★★★★★<br />
    <input name="rating" type="radio" value="4"/> ★★★★☆<br />
    <input name="rating" type="radio" value="3"/> ★★★☆☆<br />
    <input name="rating" type="radio" value="2"/> ★★☆☆☆<br />
    <input name="rating" type="radio" value="1"/> ★☆☆☆☆<br />
    <input name="orderinfo" type="hidden" value="{order_identity}" />
    <p style="padding-left:2%">
        <input type="submit" value="Submit" style="background-color: #f0ad4e; height:27px; color:white; border-radius:2px;
cursor: pointer; cursor: hand; border-width:0;">
    </p>
</form>
<p>Thank you for using Sevame.</p>
"""