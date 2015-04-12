order_accepted_laundry = """
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
   <table class="table" style="width:100%;border: 1px solid black;border-collapse: collapse;">
      <tbody>
         <tr>
            <th style="padding:2%;border: 1px solid black; text-align: center; width: 50%;">Type of cloth</th>
            <th style="padding:2%;border: 1px solid black; text-align: center; width: 15%;">Wash</th>
            <th style="padding:2%;border: 1px solid black; text-align: center; width: 20%;">Wash+Iron</th>
            <th style="padding:2%;border: 1px solid black; text-align: center; width: 15%;">Iron</th>
         </tr>
         <tr>
            <td style="padding:2%;border: 1px solid black; text-align: center;">Regulars (Shirts,Pants,Salwars etc.)</td>
            <td style="padding:2%;border: 1px solid black; text-align: center;">18</td>
            <td style="padding:2%;border: 1px solid black; text-align: center;">25</td>
            <td style="padding:2%;border: 1px solid black; text-align: center;">7</td>
         </tr>
         <tr>
            <td style="padding:2%;border: 1px solid black; text-align: center;">Large Wearables (Sarees, Suits,Pull-Overs etc.)</td>
            <td style="padding:2%;border: 1px solid black; text-align: center;">40</td>
            <td style="padding:2%;border: 1px solid black; text-align: center;">50</td>
            <td style="padding:2%;border: 1px solid black; text-align: center;">10</td>
         </tr>
         <tr>
            <td style="padding:2%;border: 1px solid black; text-align: center;">Non-Wearables (BedSheets, Curtains etc.)</td>
            <td style="padding:2%;border: 1px solid black; text-align: center;">55</td>
            <td style="padding:2%;border: 1px solid black; text-align: center;">70</td>
            <td style="padding:2%;border: 1px solid black; text-align: center;">15</td>
         </tr>
      </tbody>
   </table>
</div>
"""