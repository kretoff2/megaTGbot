from my_libs.sql_commands import SQL_connection, SQL_one_command

needExForNewLevel = [
    10, 25, 50, 150, 250, 500, 750, 1500, 4000, 10000, 25000
]

class levelCalculate():
    def __init__(self, chatID: int | str):
        self.chatID = int(chatID)
        self.ex, self.level, self.userClass = SQL_one_command("SELECT experience, level, class FROM users WHERE chatID = ?", (chatID,), fetchMode = "one").data
        if self.userClass != None:
            self.userClass = self.userClass[0]
            status = self.calculate()
            self.status = status
            while status:
                status = self.calculate()
    def calculate(self):
        if self.level >= len(needExForNewLevel):
            return False
        if self.ex >= needExForNewLevel[self.level]:
            conn = SQL_connection()
            conn.sql_command("UPDATE users SET experience = experience - ? WHERE chatID = ?", (needExForNewLevel[self.level], self.chatID))
            conn.sql_command("UPDATE users SET level = level + 1 WHERE chatID = ?", (self.chatID,))
            conn.sql_save()
            conn.sql_close()
            self.ex -= needExForNewLevel[self.level]
            self.level += 1
            return True