order_quote_others = """
<p>Dear {customer_name}</p>

<p>Here is the Quote Estimate for {service} Order No {order_id} as given by Mr. {sp_name} after inspection.</p>
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
<p>Please use the link to finish the payment {link}</p>

"""