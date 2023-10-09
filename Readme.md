
# Requisitos:
<b>0 – </b> Have installed Python 3.9 (or higher)<br>
<b>1 – </b> Be logged in as root<br>
<b>2 – </b> Run the following commands<br>

<h3>
Install the packages:
</h3>

<p> Debian/Ubuntu</p> 
<pre>sudo apt-get install -y wget dos2unix git sudo curl bc python3-pip</pre>

<p>Download the installation script</p>
<pre>cd /tmp ; wget https://raw.githubusercontent.com/bernardolankheet/trmm-telegram/main/install.sh -O install.sh ; sudo dos2unix install.sh ; sudo bash install.sh</pre>


<h3>
Telegram
</h3>
<b>0 – </b> Create a Bot token with BotFather on Telegram<br>
<b>1 – </b> Get userID or usergroupID to send menssage<br>

<h3>
Change options on configScrips.ini
</h3>

<pre>
# URL Tacticall (without subdomain rmm. mesh. or api.)
url = rmmtactical.com 
# This a apikey tacticall, Settings > Global Settings > API KEYS
alert_api_key = SVXKKBFOTOVDGU268KSIIWL88W5ZRD123RH 

#Interval in seconds check new alerts.
updateinterval = 10 
#Mumbers of IDs stored in sent_alerts.json file
max_alerts = 100 
# database storage id alerts send and resolved.
sent_alerts_file = /opt/trmm-telegram/sent_alerts.json 

# Telegram Bot Token, used https://t.me/BotFather
bot_token = 181768159672:AnsHUYgdyioLIWOt_9R24G-c9lYuwwaVeEDPKo 
# Telegram group/user ID to receive messages, used https://t.me/myidbot
user_group_telegram = 150157059
</pre>

