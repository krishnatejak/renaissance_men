laundry_picked = """
<p>Dear {customer_name}</p>
<p>The following items have been picked up from your location. </p>
<table class="table" style="width:75%;border: 1px solid black;border-collapse: collapse;">
    <tbody>
        <tr>
            <th style="padding:2%; border: 1px solid black;">Item</th>
            <th style="padding:2%; border: 1px solid black;">Quantity</th>
            <th style="padding:2%; border: 1px solid black;">Amount</th>
        </tr>
        {table_data}
    </tbody>
</table>
<p>Your total bill amount is {bill_amount}</p>
<p>Please use the link to finish the payment {link}</p>
<p>Your clothes will be delivered within 36 hours of pickup</p>
<p><b>If you find any discrepancy with either the items picked up or the bill amount please contact us.</b> </p>
"""

table_data = """
<tr>
    <td style="padding:2%; border: 1px solid black;">{item}</td>
    <td style="padding:2%; border: 1px solid black;">{quantity}</td>
    <td style="padding:2%; border: 1px solid black;">{amount}</td>
</tr>
"""