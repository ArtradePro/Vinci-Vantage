import time
import logging
import pywhatkit  # The engine for WhatsApp automation
import datetime

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

class VinciCommerceBot:
    def __init__(self):
        logging.info("Vinci-Vantage Commerce Protocol Initialized.")
        self.my_phone = "+1234567890"  # Your phone number (optional config)

    def generate_fb_listing(self, item_name, price, condition, features):
        """
        Generates a high-conversion description to copy/paste into Facebook Marketplace.
        """
        logging.info(f"Generating listing for: {item_name}")
        
        listing_text = f"""
🔥 {item_name.upper()} - GREAT CONDITION - ${price}

Selling a {condition} {item_name}. 

✅ FEATURES:
{features}

📍 Pickup Location: [City/Area]
💰 Price: ${price} (Cash or Zelle/Revolut)

First come, first served. Message me on WhatsApp if interested!
        """
        print("\n" + "="*50)
        print(listing_text)
        print("="*50 + "\n")
        logging.info("Listing generated. Copy the text above for Facebook Marketplace.")
        return listing_text

    def send_whatsapp_offer(self, seller_phone, item_name, offer_price):
        """
        Automates sending a buying offer via WhatsApp Web.
        NOTE: You must be logged into web.whatsapp.com in your default browser.
        """
        logging.info(f"Preparing offer for {item_name} to {seller_phone}...")
        
        message = (f"Hi! I saw your listing for the {item_name} on Facebook Marketplace. "
                   f"I am interested. Would you accept ${offer_price} if I pick it up today?")
        
        try:
            # Sending message instantly (wait_time is delay before typing)
            # tab_close=True tries to close the tab after sending
            pywhatkit.sendwhatmsg_instantly(
                phone_no=seller_phone, 
                message=message, 
                wait_time=15, 
                tab_close=True
            )
            logging.info("WhatsApp message sent successfully!")
        except Exception as e:
            logging.error(f"Failed to send WhatsApp message: {e}")

    def send_whatsapp_followup(self, buyer_phone, item_name):
        """
        Send a follow-up message to a potential buyer.
        """
        logging.info(f"Sending follow-up for {item_name} to {buyer_phone}...")
        
        message = (f"Hi! Just following up on the {item_name}. "
                   f"Are you still interested? I can hold it for you if you confirm today.")
        
        try:
            pywhatkit.sendwhatmsg_instantly(
                phone_no=buyer_phone, 
                message=message, 
                wait_time=15, 
                tab_close=True
            )
            logging.info("Follow-up message sent successfully!")
        except Exception as e:
            logging.error(f"Failed to send follow-up message: {e}")

    def generate_negotiation_response(self, original_price, offer_price):
        """
        Generate a counter-offer response for negotiations.
        """
        counter = (float(original_price) + float(offer_price)) / 2
        
        response = f"""
💬 Suggested Counter-Offer Response:

"Thanks for your interest! I appreciate the offer of ${offer_price}, 
but my lowest would be ${counter:.0f}. Let me know if that works for you!"
        """
        print(response)
        return response

    def run_interactive_mode(self):
        """
        Runs a menu for the user to choose actions.
        """
        print("\n" + "="*50)
        print("       🛒 VINCI-VANTAGE COMMERCE ASSISTANT 🛒")
        print("="*50)
        print("\n📤 SELLING:")
        print("  1. Generate Facebook Listing")
        print("  2. Generate Counter-Offer Response")
        print("\n📥 BUYING:")
        print("  3. Send WhatsApp Buy Offer")
        print("  4. Send WhatsApp Follow-Up")
        print("\n🚪 5. Exit")
        print("-"*50)
        
        choice = input("Select an option (1-5): ").strip()

        if choice == '1':
            print("\n--- CREATE FACEBOOK LISTING ---")
            item = input("Item Name: ")
            price = input("Price ($): ")
            cond = input("Condition (New/Like New/Good/Fair): ")
            feats = input("Key Features (comma separated): ")
            features_formatted = "\n".join([f"- {f.strip()}" for f in feats.split(",")])
            self.generate_fb_listing(item, price, cond, features_formatted)
            
        elif choice == '2':
            print("\n--- COUNTER-OFFER GENERATOR ---")
            original = input("Your Listed Price ($): ")
            offer = input("Buyer's Offer ($): ")
            self.generate_negotiation_response(original, offer)
            
        elif choice == '3':
            print("\n--- SEND BUY OFFER ---")
            print("⚠️  Make sure you're logged into web.whatsapp.com first!")
            phone = input("Seller Phone (with country code, e.g., +15550001234): ")
            item = input("Item Name: ")
            offer = input("Your Offer Price ($): ")
            confirm = input(f"Send offer of ${offer} for {item} to {phone}? (y/n): ")
            if confirm.lower() == 'y':
                self.send_whatsapp_offer(phone, item, offer)
            else:
                print("Cancelled.")
            
        elif choice == '4':
            print("\n--- SEND FOLLOW-UP ---")
            print("⚠️  Make sure you're logged into web.whatsapp.com first!")
            phone = input("Buyer Phone (with country code): ")
            item = input("Item Name: ")
            confirm = input(f"Send follow-up about {item} to {phone}? (y/n): ")
            if confirm.lower() == 'y':
                self.send_whatsapp_followup(phone, item)
            else:
                print("Cancelled.")
            
        elif choice == '5':
            logging.info("Shutting down Vinci-Vantage. Goodbye!")
            exit()
        
        else:
            print("Invalid option. Please try again.")


if __name__ == "__main__":
    bot = VinciCommerceBot()
    # Loop to keep the menu open
    while True:
        bot.run_interactive_mode()
