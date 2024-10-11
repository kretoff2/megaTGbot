
bot = None

RBClasses = ["6", "7", "8", "9"]
RFClasses = []

for el in RBClasses:
    exec(f"from my_libs.GDZClasses import RB{el}class")
def init(Lbot):
    global bot
    bot = Lbot
    for el in RBClasses:
        exec(f"RB{el}class.bot = bot")
    for el in RFClasses:
        exec(f"RF{el}class.bot = bot")
def route_gdz_0(call, gos = "RB"):
    data = call.data
    userClass = data.split(":")[1]
    if not check_class(gos, userClass):
        bot.send_message(call.message.chat.id, "Для вас недоступно гдз")
        return
    exec(f"{gos}{userClass}class.route_gdz_0(call)")
def route_gdz_s(call, gos = "RB"):
    data = call.data
    userClass = data.split(":")[1]
    if not check_class(gos, userClass):
        bot.send_message(call.message.chat.id, "Для вас недоступно гдз")
        return
    exec(f"{gos}{userClass}class.gdz_s_{userClass}(call)")

def check_class(gos, userClass):
    if gos == "RB" and userClass in RBClasses: return True
    elif gos == "RF" and userClass in RFClasses: return True
    return False