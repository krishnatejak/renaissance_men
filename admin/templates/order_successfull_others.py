order_successful_others_template = """
<p>Dear {customer_name}</p>
<p>Thank you for using <b>Sevame</b>. Your {service} order for {request} has been placed successfully.</p>
<div style="padding-left:5%">
    <p><b>Order Details:</b></p>
    <p>Order Number: {order_id}</p>
    <p>Arrival Time: {pickup_time}</p>
    <p>Address: {order_address}</p>
    <p>Phone Number: {phone_number}</p>
</div>
<p>Minimum Bill amount is Rs 200.</p>
<p>For Minor Checks and Fixes : Rs 200 + Material Cost.</p>
<p>A Quote Estimate will be sent to you via email after our technician takes a look at the problem.</p>

"""