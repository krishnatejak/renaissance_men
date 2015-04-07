order_accepted_laundry = """
<style type="text/css">
    td {{
         padding:2%;
         border: 1px solid black;
    }}
</style>
<p>Dear {customer_name}</p>
<p>Thank you for using <b>Sevame</b>. Your {service} order for {request} has been placed successfully.</p>
<div style="padding-left:5%">
    <p><b>Order Details:</b></p>
    <p>Order Number: {order_number}</p>
    <p>Pickup Time: {pickup_time}</p>
    <p>Pickup Address: {order_address}</p>
    <p>Phone Number: {phone_number}</p>
</div>
<p>Our executive will get in touch with you before the pickup and delivery of the clothes. Your ordered will be fulfilled in 36 hours.</p>
<div class="panel panel-default" style="color:">
   <!-- Default panel contents -->
   <div class="panel-heading">
        <p><b>Pricing</b></p>
    </div>
   <table class="table" style="border: 1px solid black">
      <tbody>
         <tr>
            <td><strong>Type of cloth</strong></td>
            <td>Wash+Iron</td>
            <td>Iron</td>
         </tr>
         <tr>
            <td><strong>Regulars</strong> (Shirts,Pants,Salwars etc.)</td>
            <td>25</td>
            <td>7</td>
         </tr>
         <tr>
            <td><strong>Large Wearables</strong> (Sarees, Suits,Pull-Overs etc.)</td>
            <td>50</td>
            <td>10</td>
         </tr>
         <tr>
            <td><strong>Non-Wearables</strong> (BedSheets, Curtains etc.)</td>
            <td>70</td>
            <td>15</td>
         </tr>
      </tbody>
   </table>
</div>
"""