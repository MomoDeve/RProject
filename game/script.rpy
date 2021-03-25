init python:
    import random

    class player:

        def __init__(self, level, xp, update_func):
            self.level = level
            self.xp = xp
            self.points = self.max_points = 0
            self.health = self.max_health = 0
            self.min_damage = self.max_damage = 0
            self.damage_mult = self.attack_mult = 1.0
            self.attacks = []
            self.attacks_log = []
            self.update_func = update_func
            self.calc_stats()

        def calc_stats(self): #calculating stats using level and current xp
            self.max_health = self.health = self.level * 50 + 50
            self.max_points = self.points = self.level // 5 + 1
            self.min_damage = self.level * 8 + 7
            self.max_damage = self.min_damage * 2
            self.damage_mult = self.attack_mult = 1.0

        def add_xp(self, xp): #returns true if player reached new level
            self.xp += xp
            needed_xp = (100 + 100 * self.level) // 2 * self.level
            if self.xp >= needed_xp:
                self.level += 1
            self.calc_stats()
            return self.xp >= needed_xp

        def take_damage(self, damage): #returns damage
            dmg = int(self.damage_mult * damage)
            self.health -= dmg
            return dmg

        def is_dead(self):
            return self.health <= 0

        def get_attack(self, id):         # {-1} Base Attack
            self.attacks_log.append(id)   # {-2} Block
            if id == -1:                  # {-3} Waiting
                return self.base_attack() # {0 - x} Skill Attack
            elif id == -2:
                self.damage_mult = 0.5
            elif id == -3:
                self.damage_mult = 1.5
            else:
                return self.attacks[id]

        def base_attack(self):
            return int(self.attack_mult * random.randint(self.min_damage, self.max_damage))

        def last_attack(self):
            if len(self.attacks_log) < 1:
                return 0
            else:
                return self.attacks_log[len(self.attacks_log) - 1]

    class enemy:

        def __init__(self, name, health, update_func, rand_func, text_params = "m"): #m - male, f - female, t - they, i - it
            self.max_health = self.health = health
            self.name = name
            self.attacks = []
            self.attacks_log = []
            self.text_params = text_params
            self.update_func = update_func
            self.get_rand = rand_func

        def take_damage (self, damage): #returns damage
            self.health -= damage
            return damage

        def is_dead(self):
            return self.health <= 0

        def get_attack(self, id):
            if id < 0:
                id = -id
            self.attacks_log.append(id)
            return self.attacks[id]

        def last_attack(self):
            if len(self.attacks_log) < 1:
                return 0
            else:
                return self.attacks_log[len(self.attacks_log) - 1]

    class attack:

        def __init__(self, name, func, value = 0, cost = 0):
            self.name = name
            self.func = func
            self.value = value
            self.cost = cost

    class log:

        def __init__(self, win_func, lose_func, turn_updater, text = ""):
            self.screen_text = text
            self.turn = 0
            self.list_pos = -1
            self.text_list = []
            self.display_perks = False
            self.win = self.lose = False
            self.allow_turn = True
            self.win_func = win_func
            self.lose_func = lose_func
            self.turn_updater = turn_updater

        def set_perks_display(self, state): #set display of player's skill perks
            self.display_perks = state

        def end_of_list(self):
            self.allow_turn = (self.list_pos + 1 == len(self.text_list)) #next turn is allowed if player reached end of log list
            return self.allow_turn

        def get_text(self): #return true if list_pos reached last element
            if self.list_pos < len(self.text_list) - 1:
                self.list_pos += 1
                self.screen_text = self.text_list[self.list_pos]
            self.end_of_list()

        def fight_lose(self, p, e):
            return (self.lose_func(self, p, e) and self.end_of_list())

        def fight_win(self, p, e):
            return (self.win_func(self, p, e) and self.end_of_list())

        def start_new_turn(self, p, e, id):
            self.turn_updater(self, p, e)
            p.update_func(self, p, e)
            attack = p.get_attack(id)
            if id == -1:
                e.take_damage(attack)
                self.text_list.append("Вы нападаете!")
                self.text_list.append("Вы наносите " + str(attack) + " урона!")
            elif id == -2:
                self.text_list.append("Вы встаёте в защитную стойку")
            elif id == -3:
                self.text_list.append("Вы ждёте атаки противника")
            else:
                p.points -= attack.cost
                self.text_list.append("Использован приём " + attack.name)
                attack.func(attack, self, p, e)
            if not self.win_func(self, p, e):
                self.end_turn(p, e)
            self.get_text()

        def end_turn(self, p, e):
            value = e.update_func(self, p, e)
            if value >= 0:
                value = e.get_rand(self, p, e)
            attack = e.get_attack(value) # value converts to positive
            attack.func(attack, self, p, e)
            if not self.lose_func(self, p, e):
                self.text_list.append("Ваш ход!")

        def clear_indicator(self, T, value = 0): #adds element (usually zero) to attack list (after indicator)
            T.attacks_log.append(value)

############################################# std functions #######################################################################

    def std_log_update(log, p, e):
        log.turn += 1
        log.allow_turn = False
        log.text_list = []
        log.list_pos = -1

    def std_player_update(log, p, e):
        p.attack_mult = p.damage_mult = 1.0
        if (p.last_attack() <= 0) and (p.max_points > p.points):
            p.points += 1

    def std_enemy_update(log, p, e):
        return e.last_attack()

    def std_win_check(log, p, e):
        if not log.win and e.is_dead():
            str_value = e.name
            log.win = True
            if e.text_params == "f":
                str_value += " повержена!"
            elif e.text_params == "t":
                str_value += " повержены!"
            elif e.text_params == "i":
                str_value += " повержено!"
            else:
                str_value += " повержен!"
            log.text_list.append(str_value)
        return log.win

    def std_lose_check(log, p, e):
        if not log.lose and p.is_dead():
            log.lose = True
            log.text_list.append("Вы погибли!")
        return log.lose

    def std_enemy_rand(log, p, e):
        if (log.turn + 1) % 5 == 0 and len(e.attacks) > 3: # {0 - 2} base attacks, {3 - 4} block attack {5 - 6} wait attack {7} heal
            return -3
        elif log.turn > 7 and e.health < e.max_health // 2 and random.choice([True, False]) and len(e.attacks) > 7:
            return -7
        elif(random.randint(0, 5) == 5 and len(e.attacks) > 5):
            return -5
        else:
            return random.randint(-2, 0)

    def std_base_attack(attack, log, p, e):
        log.text_list.append(attack.name)
        if p.last_attack() == -2:
            log.text_list.append("Вы заблокировали часть получаемого урона!")
        damage = attack.value + random.randint(-1 * attack.value // 5, attack.value // 5) # 20% random
        if damage < 0:
            return
        if e.text_params == "t":
            log.text_list.append(e.name + " наносят " + str(int(p.damage_mult * damage)) + " урона!")
        else:
            log.text_list.append(e.name + " наносит " + str(int(p.damage_mult * damage)) + " урона!")
        p.take_damage(damage)

    def std_block_attack(attack, log, p, e):
        log.text_list.append(attack.name)
        e.attacks_log.append(-4) #indicator of block attack
        if attack.value <= 0:
            return
        if p.last_attack() == -2:
            log.text_list.append("Вы заблокировали часть получаемого урона!")
        damage = attack.value + random.randint(-1 * attack.value // 5, attack.value // 5) # 20% random
        if damage < 0:
            return
        if e.text_params == "t":
            log.text_list.append(e.name + " наносят " + str(int(p.damage_mult * damage)) + " урона!")
        else:
            log.text_list.append(e.name + " наносит " + str(int(p.damage_mult * damage)) + " урона!")
        p.take_damage(damage)

    def std_wait1_attack(attack, log, p, e):
        log.text_list.append(attack.name)
        e.attacks_log.append(-6) #indicator of wait attack

    def std_wait2_attack(attack, log, p, e):
        log.clear_indicator(e)
        if p.last_attack() == -3:
            log.text_list.append("Противнику не удалось обмануть вас")
            return
        log.text_list.append(attack.name)
        if p.last_attack() == -2:
            log.text_list.append("Вы заблокировали часть получаемого урона!")
        else:
            log.text_list.append("Вас застали врасплох!")
        damage = attack.value + random.randint(-1 * attack.value // 5, attack.value // 5) # 20% random
        if damage < 0:
            return
        if e.text_params == "t":
            log.text_list.append(e.name + " наносят " + str(int(p.damage_mult * damage)) + " урона!")
        else:
            log.text_list.append(e.name + " наносит " + str(int(p.damage_mult * damage)) + " урона!")
        p.take_damage(damage)

######################################################### game skills ##########################################################
    def duel_win(log, p, e):
        if not log.win and (p.is_dead() or e.is_dead()):
            log.win = True
            log.text_list[len(log.text_list) - 1] = "Дуэль окончена!"
        return log.win

    def wait10turns_check(log, p, e):
        if log.turn == 10 and not log.win:
            log.win = True
            e.health -= 500000
            log.text_list.append("Огромная вспышка заполняет весь зал!")
            log.text_list.append("Сэр Штрауф использует Разрушитель Небес!")
            log.text_list.append("Ледяное Порождение получает 500000 урона!")
            log.text_list.append("Ледяное Порождение повержено!")
        return log.win

    def duel_lose(log, p, e):
        return False

    def max_heal_skill(attack, log, p, e):
        e.health = e.max_health
        log.text_list.append("Противник полностью восстанавливает своё здоровье!")

    def heaven_destroyer(attack, log, p, e):
        if len(e.attacks_log) != 0 and e.attacks_log[len(e.attacks_log) - 1] == -4:
            log.text_list.append("Меч Штрауфа пронзает само небо своим\nпламенем и вонзается в тело противника!")
            log.text_list.append("Вы наносите " + str(e.health) + " урона!")
            e.take_damage(e.health)
        else:
            damage = int(p.attack_mult * (attack.value + random.randint(-1 * attack.value // 5, attack.value // 5)))
            log.text_list.append("Вы наносите " + str(damage) + " урона!")
            e.take_damage(damage)

    def sample_attack(attack, log, p, e):
        damage = int(p.attack_mult * (attack.value + random.randint(-1 * attack.value // 5, attack.value // 5)))
        e.take_damage(damage)
        log.text_list.append("Вы наносите " + str(damage) + " урона!")

    def lightning_attack(attack, log, p, e):
        if log.turn == 1:
            log.text_list.append("Получен бонус к урону!")
            p.attack_mult *= 2
        else:
            p.attack_mult *= 0.5
        damage = int(p.attack_mult * (attack.value + random.randint(-1 * attack.value // 10, attack.value // 10)))
        e.take_damage(damage)
        log.text_list.append("Вы наносите " + str(damage) + " урона!")

    def tornado_attack(attack, log, p, e):
        damage = int(p.attack_mult / 4 * attack.value)
        for i in range(4):
            dmg = damage + random.randint(0, damage // 7)
            e.take_damage(dmg)
            log.text_list.append("Вы наносите " + str(dmg) + " урона!")

    config.has_autosave = True
    config.autosave_slots = 1
    config.autosave_on_choice = True
    config.autosave_on_quit = True

    def display_death_screen():
        renpy.hide_screen("fight_screen")
        renpy.scene()
        renpy.show("bg death")
        renpy.show_screen("death_screen")

init:
    style rpg_hud_button:
        background im.Scale("gui/button/choice_idle_background.png", 300, 30)
        hover_background im.Scale("gui/button/choice_hover_background.png", 300, 30)
        xsize 300
        ysize 30
    style rpg_skill_button:
        background im.Scale("gui/button/choice_idle_background.png", 500, 50)
        hover_background im.Scale("gui/button/choice_hover_background.png", 500, 50)
        xsize 500
        ysize 50

    screen fight_screen(Log, p, e):

        textbutton "": #text display
            yalign 0.91
            text_color "000000"
            xsize 1280
            ysize 128
            background im.Scale("gui/textbox.png", 1280, 128)
            #multiple actions: end fight or get next line
            if Log.fight_win(p, e):
                action Return()
            elif Log.fight_lose(p, e):
                action Function(display_death_screen)
            else:
                action Function(Log.get_text)

        label Log.screen_text:
            text_color "000000"
            yalign 0.855
            xalign 0.5

        bar:
            value p.health
            range p.max_health
            xsize 450
            ysize 57
            yalign 0.8
        label "[p.health] / [p.max_health]":
            text_color "000000"
            yalign 0.79
            xalign 0.01
        label "Очки способностей: [p.points] / [p.max_points]":
            text_color "99ff33"
            yalign 0.73
            xalign 0.01

        bar:
            value e.health
            range e.max_health
            xsize 450
            ysize 57
        label "[e.health] / [e.max_health]":
            text_color "000000"
            yalign 0.02
            xalign 0.01
        label "[e.name]":
            text_color "000000"
            text_xalign 0
            yalign 0.045
            xalign 0.35

        if not Log.display_perks:
            hbox:
                spacing 0
                yalign 0.97
                xalign 0.5

                textbutton "Атаковать":
                    style "rpg_hud_button"
                    text_color "4d4d4d"
                    text_hover_color "000000"
                    text_xalign 0.5
                    text_yalign 0.5
                    text_layout "nobreak"
                    if Log.allow_turn:
                        action Function(Log.start_new_turn, p, e, -1)

                textbutton "Защищаться":
                    style "rpg_hud_button"
                    text_color "4d4d4d"
                    text_hover_color "000000"
                    text_xalign 0.5
                    text_yalign 0.5
                    text_layout "nobreak"
                    if Log.allow_turn:
                        action Function(Log.start_new_turn, p, e, -2)

                textbutton "Ждать":
                    style "rpg_hud_button"
                    text_color "4d4d4d"
                    text_hover_color "000000"
                    text_layout "nobreak"
                    text_xalign 0.5
                    text_yalign 0.5
                    if Log.allow_turn:
                        action Function(Log.start_new_turn, p, e, -3)

                textbutton "приёмы":
                    style "rpg_hud_button"
                    text_color "4d4d4d"
                    text_hover_color "000000"
                    text_layout "nobreak"
                    text_xalign 0.5
                    text_yalign 0.5
                    action Function(Log.set_perks_display, True)

        else:
            vbox:
                spacing 0
                yalign 0.05
                xalign 0.95
                python:
                    i = 0
                for attack in p.attacks:
                    textbutton "[attack.name] ([attack.cost])":
                        style "rpg_skill_button"
                        text_color "4d4d4d"
                        text_hover_color "000000"
                        text_layout "nobreak"
                        text_xalign 0.5
                        text_yalign 0.5
                        if attack.cost <= p.points and Log.allow_turn:
                            action Function(Log.start_new_turn, p, e, i)
                    python:
                        i += 1

                textbutton "назад":
                    style "rpg_skill_button"
                    text_color "4d4d4d"
                    text_hover_color "000000"
                    text_layout "nobreak"
                    text_xalign 0.5
                    text_yalign 0.5
                    action Function(Log.set_perks_display, False)

    screen death_screen():
        textbutton "Нажмите для загрузки последнего сохранения":
            action Function(renpy.reload_script)
            yalign 0.95
            xalign 0.5
        label "Вы проиграли бой и трагически погибли":
            text_color "808080"
            yalign 0.88
            xalign 0.5

image Red = "images/Red.png"
image Host = "images/Host.png"
image Ted_Gensin = "images/Ted_Gensin.png"
image Wingerm = "images/Wingerm.png"
image Diogen = "images/Diogen.png"
image Joseph = "images/Joseph.png"
image Din = "images/Din.png"
image Shtrauf = "images/Shtrauf.png"

image bg field = "images/field.png"
image bg death = "images/death.png"
image bg house_night1 = "images/house_night1.png"
image bg guesthouse1 = "images/guesthouse1.png"
image bg guesthouse2 = "images/guesthouse2.png"
image bg guesthouse_room1 = "images/guesthouse_room1.png"
image bg forest_lake = "images/forest_lake.png"
image bg black = "images/black.png"
image bg forest_village = "images/forest_village.png"
image bg forest_river = "images/forest_river.png"
image bg forest1 = "images/forest1.png"
image bg mountain_village = "images/mountain_village.png"
image bg campfire = "images/campfire.png"
image bg guild_hall1 = "images/guild_hall1.png"
image bg guild_hall2 = "images/guild_hall2.png"
image bg destroyed_village1 = "images/destroyed_village1.png"
image bg destroyed_house1 = "images/destroyed_house1.png"
image bg destroyed_church = "images/destroyed_church.png"
image bg mountains1 = "images/mountains1.png"
image bg flame_dragon = "images/flame_dragon.png"
image bg luften1 = "images/luften1.png"
image bg luften2 = "images/luften2.png"
image bg luften3 = "images/luften3.png"
image bg luften4 = "images/luften4.png"
image bg luften5 = "images/luften5.png"
image bg luften_market = "images/luften_market.png"
image bg luften_square = "images/luften_square.png"
image bg alchemist_house = "images/alchemist_house.png"
image bg joseph_house1 = "images/joseph_house1.png"
image bg joseph_house2 = "images/joseph_house2.png"
image bg dead_lands1 = "images/dead_lands1.png"
image bg castle1 = "images/castle1.png"
image bg Vaal_first = "images/Vaal_first.png"
image bg Vaal_second = "images/Vaal_second.png"
image bg Cvain = "images/Cvain.png"
image bg vault = "images/vault.png"
image bg sewage1 = "images/sewage1.png"
image bg sewage2 = "images/sewage2.png"
image bg dark_village = "images/dark_village.png"
image bg luften_gates = "images/luften_gates.png"
image bg luften_palace = "images/luften_palace.png"

define red = Character('Ред: ', color="#cc0000")
define host = Character('Хозяин таверны: ', color="#000066")
define tedg = Character('Тед Гензин: ', color='#9966ff')
define villager = Character('Житель: ', color='#666666')
define djoun = Character('Джоун: ', color='#04ccee')
define wingerm = Character('Вингерм: ', color='#990000')
define diogen = Character('Диоген: ', color='#0033cc')
define joseph = Character('Йозеф: ', color='#6666ff')
define tormod = Character('Тормод: ', color='#008000')
define shtrauf = Character('Сэр Штрауф: ', color="#000066")
define vaal = Character('Ваал: ', color="#3c9eff")
define banker = Character('Банкир: ', color="#000000")

define ask_counter1 = False
define ask_counter2 = False
define ask_counter3 = False
define ask_counter4 = False

define stage = "Начало"
define chapter = 1

label start:
    $ stage = "Начало"
    $ chapter = 1
    $ save_name = "Глава " + str(chapter) + ". " + stage
    scene bg field with fade
    "Солнце..."
    "Трава..."
    "Вдали слышится пение птиц"
    "Как хорошо. Так бы и лежал весь день"
    "Но почему я чувствую, будто что-то не так? Что же могло такого произойти?"
    "А что, собственно было? Где я вообще?"
    show Red with dissolve
    "Старик: " "О, привет, что лежим?"
    "Что... Где я?"
    "Старик: " "Как где? В Луфтене!"
    "Л... Луфтене?"
    "Старик: " "Ну да, вставай, давай помогу\nТебя кстати как звать?"
    "Зовут..?"
    define name = ""
    while name == "":
        $ name = renpy.input("Вспомните своё имя:")
        $ name = name.strip()
    define me = Character('[name]', color="#000000")
    define level = 1
    define xp = 0
    me "Меня зовут [me]. А вы кто?"
    red "Можно на ты. Меня Ред зовут, я торговец местный"
    red "Вот иду в город товар продать, а тут ты на земле лежишь"
    red "Ну я и думаю: \"разбужу парня, что он на дороге валяется\""
    me "Спасибо. Только вот похоже, я ничего не помню, ни как попал сюда, ни где я вообще"
    red "О, ну это не беда. Если что не знаешь - спрашивай, помогу, чем смогу!"

    define expl_choice1 = False
    define expl_choice2 = False
    define expl_choice3 = False

label red_world_explanation:
    if expl_choice1 and expl_choice2 and expl_choice3:
        jump guesthouse
    menu:
        "Где мы сейчас находимся?" if not expl_choice1:
            $ expl_choice1 = True
            me "Можешь рассказать, где мы сейчас? Я совершенно не помню, что это за мир"
            red "Мда, тяжёлый случай. Ну что же, поздравляю, ты в Инзеле!"
            red "Инзель - континент, населённый людьми, эльфами, троллями и всякими другими существами"
            red "Издавна его делят между собой три королевства, в одном из которых мы сейчас и находимся"
            red "Однако, большая часть континента до сих пор остаётся неизведанной, так что не стоит удивляться, если наткнешся на какого-нибудь ранее невиданного никому монстра, если пойдешь в ближайший лес"
            red "В городах или близ дорог по большей части спокойно, разве что стоит опасаться бандитов, но в сейчас Луфтене их почти нет"
            jump red_world_explanation
        "Расскажи мне про Луфтен" if not expl_choice2:
            $ expl_choice2 = True
            me "Расскажи мне про Луфтен. Ты упомянул его несколько раз, но я пока не имею представления, что это за город"
            red "Ооо, Луфтен - огромное королевство и в тоже время название его столицы"
            red "Луфтен является самым влиятельным королевством на всём материке"
            red "Расположен он на северо-западе и, спустя более 1000 лет с основания, разросся до небывалых размеров, охватив обширные территории вплоть до Великого Хребта"
            me "Великий Хребет?"
            red "Да, это большая горная цепь, проходящая по центру материка. В целом, туда стараются  не ходить, потому что близ гор живёт много опасных существ"
            red "Я могу потом рассказать, если хочешь. А что до Луфтена..."
            red "Столица королевства представляет для меня наибольший интерес, как, впрочем, и для всех других торговцев"
            red "В городе можно найти разнообразные товары, работу, врагов и друзей"
            red "Если же нужно отправиться в одно из других королевств, можно поискать корабль в Луфтенском порту"
            red "К счастью, правитель Луфтена, Эрлих II, поддерживает доброжелательные отношения со всеми странами и это не составит больших проблем"
            jump red_world_explanation
        "Есть ли поблизости другие города?" if not expl_choice3:
            $ expl_choice3 = True
            me "Так кроме Луфтена есть другие города или королевства?"
            red "Да, конечно. Ещё есть Мариэн, расположенный на юге материка, и Фандер, на севере"
            red "Если я начну рассказывать тебе про них детально, то боюсь мы тут до утра просидим, так что ограничусь кратким рассказом"
            red "Мариэн - королевство магов и алхимиков, представляющее из себя огромный город, расположенный на склоне горы"
            red "Это одна из самых старых стран, обладающая одновременно и самыми обширными знаниями во многих областях"
            red "Были бы деньги, обязательно туда бы съездил...\nНо сейчас не об этом"
            red "Фандер, наоборот, самое маленькое из трёх королевств, ему где-то 800 лет"
            red "Люди в нём в основном заняты кузнечным делом или работают в качестве наёмников"
            red "Его правитель, Имер IV, широко известен во всем мире, как самый суровый правитель"
            red "В стране стоит тоталитарный режим, так что я бы не советовал лишний раз туда кататься"
            jump red_world_explanation

label guesthouse:
    $ expl_choice1 = False
    $ expl_choice2 = False
    $ expl_choice3 = False

    red "..."
    red "Что-то я с тобой заговорился. Темнеть начинает"
    red "Ну, видимо, тебе со мной идти придётся, пропадешь иначе.\nДеньги хоть есть?"
    "Деньги? Точно, у меня должно быть хоть немного..."
    "Я похлопал себя по карманам и нашел в одном из них пару серебряных монет"
    me "Вот, есть парочка"
    red "Мда, немного. Ну, на ночь в какой-нибудь  ближайшей таверне хватит, а там поглядим"
    me "Поглядим это как? Нужно наверное работу найти..."
    red "А, да с этим не проблема. Возмёшь квест у ближайшей доски объявлений, я может даже помогу, если награду пополам разделим, хе"
    me "Кого взять? За что награда?"
    red "Ну квест, задание. Помочь кому-то, найти что-либо, монстра убить там. Ничего сложного"
    me "Монстра убить?!"
    red "Ох, чего кричишь. Не обязательно брать такие задания, есть много вполне простых. И все равно прибыльно"
    red "Я бы тоже с радостью выполнял квесты, да только одному сложно, я уже не молод, сил прежних нет..."
    me "Ладно, только что-то мне всё равно не верится"
    hide Red
    scene bg house_night1 with fade
    "Мы прошли с Редом несколько километров по дороге, ведущей близ красивых лесистых холмов"
    "Тропа петляла вверх вниз, огибая овраги и ручьи, пересекаясь с другими дорогами, уходящими в глубокий лес"
    "Казалось, что этому старику уже лет за 60, и кажется, для таких мест возраст этот уже не малый"
    "Но я чувствовал, что к концу нашего пути я устал гораздо больше, чем он"
    "В ногах ломило и хотелось лечь на мягкую постель и просто уснуть"
    "Я так и не смог понять, что со мной произошло, и как я оказался лежачим на дороге"
    "Будто все воспоминания о мире пропали, и остались лишь какие-то блеклые пятна"
    "Я помнил многие слова, понимал законы и природу этого мира, но все равно чувствовал себя ребенком"
    "Ребенком, которого оставили одного в огромном суровом мире, ребенком, которого приютил старик из жалости"
    "Надеюсь я не навязываюсь Реду. Он сам предложил мне помощь, и я не мог отказаться, иначе бы пропал"
    "Нужно скорее понять, как можно раздобыть денег на еду, чтобы не чувствовать себя обузой"
    "Мы остановились в небольшом трактире на обочине, и зашли внутрь уже слегка обветшалого здания"
    "Ред сказал, что это самое приемлемое место из всех поблизости, и я не стал особо возражать"
    scene bg guesthouse1 with fade
    show Red at right with dissolve
    show Host at left with moveinleft
    host "О, посетители в столь поздний час?\nСколько вас будет?"
    red "Двое, как видите. Нам комнату, пожалуйста.\nИ желательно подешевле, мы тут на одну ночь"
    host "Комнату найдём, помимо этого есть ещё какие-то пожелания?"
    red "Стакан чего-нибудь крепкого, если нетрудно"
    host "Сейчас налью. Вы пока располагайтесь за ближайшим столиком. Заодно поищу ключ от подходящей комнаты"
    hide Host with moveinright
    red "Пойдем, сядем?"
    me "Э... Да, наверное"
    show Red at center with moveinright
    "Мы прошли в угол зала и сели за старый дубовый стол, давно покрывшийся толстым слоем пыли"
    "Старик сначала о чём-то усердно думал, не сводя глаз с огонька на свечке, стоявшей за соседним столом"
    "А потом перевел взгляд на меня, будто вспоминал, кто я такой"
    "Мы встретились взгядами и неловко таращились друг на друга секунд пять"
    red "Память не вернулась, м?"
    me "А? Н-нет, если честно, я до сих пор ничего не помню"
    red "Чтож, печально. Ну ладно, что есть, то есть"
    "Ред достал кошелёк и высыпал горку монет на стол"
    red "Тут несколько десятков серебрянных. Это не так уж и много, но на ночь и еду хватит"
    red "Одна серебрянная монета эквивалентна буханке хлеба. Сто серебряных это столько же, сколько и одна золотая"
    red "Слушаешь?"
    me "Да, внимательно! А сколько можно получить за выполнение какого-нибудь задания?"
    red "Ну как тебе сказать... Когда как. Тебе бы я не советовал рассчитывать на большие суммы"
    red "Если клиент злой, то скорее всего даст не больше десятка серебром"
    red "Ну если щедрый, а таких мало, то может и пару золотых"
    me "Ого, это уже вполне приличная сумма!"
    red "Ха, да. Было время, я монеты горами грузил, некуда девать было!"
    me "Правда что ли?\nЧто-то не особо вериться..."
    red "Ну и не верь. Но так и было! Все говорили: \"Вот Ред идёт, самый богатый торговец города!\""
    red "Всё у меня было и деньги, и друзья, и девушки..."
    red "Что-то я заговорился не по делу. Эй, скоро там?"
    show Host at left with moveinleft
    host "Почти все готово, вот ваш заказ"
    "К нашему столу подошёл хозяин со стаканом виски в руках"
    host "Как вы и просили. Я нашел комнату на вас двоих на втором этаже"
    red "Спасибо. Сколько с меня?"
    host "3 серебрянных за виски, 15 за комнату, сэр"
    red "Ммгх, вот держите"
    "Ред пересчитал монеты и, положив их в мешочек, передал хозяину"
    host "Благодарю, сэр, приятного отдыха. Уже два часа ночи, поэтому я удалюсь к себе"
    host "Если что, позвоните в колокольчик на барной стойке. Я приду как только смогу"
    "Хозяин таверны открыл дверь и пошёл по коридору в одну из комнат"
    hide Host with dissolve
    me "Тут не так много посетителей. Так всегда было? Как понимаю, ты тут уже был?"
    red "Да, был несколько раз проездом. Сколько себя помню, всё примерно так и было, пустынно"
    red "Такие места не особо пользуются спросом. Это окраина, до города далеко, а ближайшие деревни не представляют интереса"
    red "Я думаю, ты жил в одной из них. Нужно проверить, может кто знает тебя"
    me "Я что-то об этом даже и не думал... Но было бы здорово!"
    "Ред улыбнулся в ответ и отпил из своего стакана"
    "Как же я сразу об этом не подумал! Если я жил в деревне, то меня обязаны помнить"
    "Я уже не первый раз ловлю себя на мысли, что совершенно не помню что со мной случилось"
    "Может быть, именно там я найду ответ на свой вопрос?"
    me "Ред, а сколько деревень поблизости?"
    red "Две или три. Я не думаю, что ты мог прийти откуда-то дальше. Их и проверим"
    red "Если повезёт, заодно сможем выполнить пару заданий, заработаем денег. Если найдём твоих родных... Ну, решим на месте"
    me "Да... Было бы здорово. Может спать пойдём, а то мы уже долго сидим?"
    red "Неплохая идея, я как раз прикончил это виски"
    "Ред встал из-за стола, взял ключ, оставленный хозяином на стойке и пошёл наверх по лестнице"
    "Я поспешил за ним, попутно размышляя о том, что нам предстоит завтра"
    scene bg guesthouse_room1 with fade
    show Red at center
    "Комната оказалась намного меньше, чем я предполагал. Две кровати, сундук, пара книжек, поросших паутиной и в принципе всё"
    red "Ну, располагайся. Сейчас уже время близистя к двум часам ночи, поэтому встанет в восемь утра"
    red "Постарайся не проспать, будить я тебя не буду. За завтраком спустишься вниз и найдешь меня на заднем дворе таверны. Всё ясно?"
    me "Да. Только зачем нам идти на задний двор, не проще ли покушать внутри?"
    red "Проще. Но тебя ждёт небольшой сюрприз от меня, ха-ха! Так что без лишних вопросов - спать"
    hide Red with fade
    "Ред, сняв только сумку и шляпу, бухнулся на кровать и мгновенно захрапел"
    "Тоже мне, сказал ждать утром сюрприза, и при этом предлагает тут же уснуть"
    "Ну и старик. Весёлый однако, с ним не заскучаешь. Даже расставаться не хочется..."
    "Эх, ладно, поживём - увидим. Надо как следует выспаться перед очередным трудным днём"
    show bg black with dissolve
    "Я тоже лёг на кровать и поразмыслив о чём-то минут пять, погрузился в глубокий сон"
    "Сон... Как же хорошо, наконец-то заслуженный отдых"
    show bg guesthouse_room1 with dissolve
    me "А? Ред? Сколько сейчас времени?"
    "Я не заметил как пролетели часы сна. Когда я встал, комната была уже пуста. Даже вещей Реда уже не было"
    "Я подошёл к стене, на которой висели старые маятниковые часы, тоже заросшие паутиной"
    me "Не похоже, что сейчас 4 ночи или утра, видимо они уже давно не ходят. Что, впрочем, и следовало ожидать"
    me "Ну что же, пойду вниз. Может найду хозяина и спрошу, давно ли встал Ред"
    "Вещей у меня не было, поэтому я просто вышел из комнаты и направился вниз по лестнице в холл"
    show bg guesthouse1 with fade
    show Host at center
    host "Доброе утро. Ваш товариш уже передал мне ключ, поэтому можете не волноваться за комнату"
    "Хорошо, хозяин здесь. Хоть у него можно спросить, давно ли тут был Ред"
    me "Да, спасибо, вы, кстати, давно его видели?"
    host "Дайте-ка подумать... Часа два назад, я полагаю. Он сказал, что подышит свежим воздухом и вышел на задний двор таверны"
    me "Два часа?! Сколько сейчас времени?"
    host "Половина десятого, сэр. Не желаете позавтракать?"
    me "Н-нет, спасибо, мне надо... надо идти!"
    host "Как пожелаете"
    "Чёрт, я всё же проспал! Подвела меня моя интуиция. Ох Ред наверное будет недоволен"
    "Так, нужно скорее пройти на задний двор"
    hide Host
    show bg forest_lake with fade
    show Red at center
    red "Ты проспал."
    me "Да... Так уж вышло, прости меня. Я правда очень устал вчера, да и вообще я как-то неважно себя чувствую"
    red "Эх, ладно, я всё равно особо не спешил, просто не хотел один завтракать"
    "Ред уселся на камень и достал из сумки пару свёртков"
    red "Держи, тут пара ломтиков хлеба с маслом. Они, конечно, уже не совсем свежие, но питаться можно"
    "Ред протянул мне один из свёртков, а сам раскрыл свой и начал жадно уплетать приготовленный им завтрак"
    me "Спасибо, Ред, я всю ночь о еде думал. Она мне даже снилась, наверное"
    red "Ммрм, ну да, ты же давно не ел. Кажется, с тех пор, как я тебя нашёл"
    "Ред промычал фразу с набитым ртом и продолжил жевать кусок хлеба"
    "Я следуя его примеру, тоже вцепился в свой долгожданный ломоть"
    "Не скажу, что он был вкусный, но счастью моему тогда не было предела"
    "Я так давно не ел... Я даже не помню, ел ли я вообще. Наверное да, но как же так? Забыть даже это?"
    me "Слушай, Ред, так что за сюрприз? Он как-то связан с тем, что ты позвал меня к этому пруду?"
    red "А, да. Я чуть не забыл. Я тут тебе кое-что приготовил, ты только не пугайся"
    "Старик наклонился, и вытащил из под камня ножны вместе с небольшим поржавевшим мечом"
    me "Это меч? Ред, я кажется тебя не совсем понимаю... Зачем он мне?"
    red "Знаешь, в путешествиях и на заданиях очень важно уметь постоять за себя. Я вроде это уже говорил"
    me "Да, но я же не умею обращаться с мечом!"
    red "Ничего, раз я до сих пор умею, значит и ты сможешь. За само оружие не переживай, его отдал хозяин таверны за пару серебряных"
    red "Он уже поржавел, но всё еще достаточно острый, чтобы порезаться. Так что аккуратней"
    "Ред протянул мне ножны, я аккуратно взял их и привязал к ремню"
    me "Он на удивление не такой уж и тяжёлый. Даже вполне себе ничего"
    red "Вот и отлично. Давай тогда, попробуй его достать и помахать. Только не задень бедного старика"
    me "Постараюсь... Опа!"
    "Я взялся за рукоятку и резким движением выдернул меч из ножен. Схватив его в обе руки, я встал, как мне показалось, в боевую стойку"
    red "О, весьма неплохо. Ты раньше явно уже дрался на мече. Немного поровнее держи ноги, и вполне сносно!"
    red "Так, хорошо, теперь попробуй сделать несколько прямых взмахов. Давай! Раз!"
    "Я взмахнул мечом и рубанул по воздуху. Затем сделал это ещё раз"
    me "Ну как? Хорошо получается? У меня и правда чувство, будто я когда-то это уже делал"
    red "Нормально, но надо ещё поработать. Попробуй вкладывать побольше веса в удары, чтобы они были сильнее"
    red "Только не переусердствуй, иначе быстро устанешь. В бою нужно уметь держать выносливость достаточно долго"
    me "Принято. Я уже начинаю понимать как точно это работает. Всё намного легче, чем я представлял"
    "Мы тренировались с Редом около часа. Советы старика, который с виду никогда бы и не взял в руки меч, оказались действительно очень полезны"
    "Я выучил пару простеньких атак мечом, а также как блокировать атаки с его помощью. То ли это так повлияла еда, то ли ещё что, но я чувствовал силу в своих руках"
    red "Отлично, молодец. Я прямо горжусь тобой, парень!"
    me "Спасибо тебе, Ред. Но я кстати заметил, что ты всё чаще смотришь куда-то в сторону. Что-то случилось?"
    "Ред действительно постоянно смотрел в сторону леса. Этио показалось мне весьма странным и даже немного подозрительным"
    red "Ничего не случилось. Но твои умения стоит проверить на практике, не находишь?"
    me "На практике? Это как, дерево предлагаешь колотить? Не с тобой же на мечах драться!"
    red "Не со мной. Убери пока меч и иди за мной, я кое-что тебе покажу. Но будь наготове в случае чего"
    "Ред направился в сторону леса, аккуратно шагая по тропинке. Я последовал за ним"
    "мы прошли вдоль нескольких поваленных деревьев, взобрались на небольшой холм. По пути старик не произнёс ни слова"
    red "Ты будешь драться с настоящим врагом, понял? Будь аккуратен и помни всему тому, чему я тебя научил, хорошо?"
    me "Хорошо, но что за враг? В этом лесу есть монстры или разбойники? С кем мне придётся сражаться?"
    red "Скорее всего с волком. Ты же знаешь волков? Это ну как собаки, только серые и не совсем дружелюбные"
    me "Я знаю кто такие волки. Мне его убить придётся этим мечом, да? И ты помогать не будешь?"
    "Из чащи послышался вой. Ред остановился и посмотрел на меня оценивающим взглядом"
    red "Я буду наблюдать за тобой из-за этого холма неподалёку. Но я могу не успеть помочь тебе в случае чего, так что в первую очередь рассчитывай на себя, а не на меня"
    red "Волки достаточно малы и не опасны по одиночке, ты особо не пугайся, во всяком случае пока он будет один"
    red "Постарайся убить его как можно быстрее, это лучшая стратегия. Ты можешь пытаться защищаться, но боюсь, проще ринуться в бой и убить врага в несколько ударов"
    me "Я тебя примерно понял. Давай, я буду ждать его здесь, а ты прячься"
    red "Удачи парень, я верю в тебя! Не облажай и сосредоточься на своём мече. Как только закончишь, дай знать"
    hide Red with dissolve
    "Ред побежал к ближайшему холму. Я остался стоять один на поляне, но уже слышал шум из кустов. Я был готов. Готов принять вызов судьбы"
    "Я услышал рык в нескольких метрах от себя. Не успел я опомниться, как противник уже был рядом"
    image wolf1 = "images/wolf1.png"
    show wolf1 with moveinbottom

    "Прямо передо мной появился большой серый волк!"
    me "Так вот ты какой... Ну давай, нападай, зверюга!"
    "Вздоргнув, я сначала чуть не выронил меч. Но вовремя сосредоточившись, взял себя в руки и встал на готове"
    "Я помню, что мне говорил Ред. Убить как можно быстрее, крепко держать меч в руках и не сомневаться. Нападаю!"

    $ renpy.block_rollback()

    define wolf1 = None
    define Player = None
    define Log = None

    define attacks = []
    $ attacks.append(attack("Волк нападает, вцепляясь в руку зубами!", std_base_attack, 10, 0))
    $ attacks.append(attack("Волк делает резкий рывок вперёд!", std_base_attack, 15, 0))
    $ attacks.append(attack("Волк рычит и бросается на вас!", std_base_attack, 10, 0))

    $ wolf1 = enemy("волк", 100, std_enemy_update, std_enemy_rand)
    $ wolf1.attacks = attacks

    $ Player = player(level, xp, std_player_update)

    $ Log = log(std_win_check, std_lose_check, std_log_update, "Началась битва с волком!")

    call screen fight_screen(Log, Player, wolf1)
    hide wolf1 with moveinbottom

    $ newLv = Player.add_xp(100)
    $ level = Player.level
    $ xp += 100

    $ renpy.block_rollback()

    "Вы получаете 100 ед. опыта!"
    if newLv:
        "Ваш уровень повышен до [level]!"
    "Не... Не может быть! У меня и правда получилось! Я смог, смог его победить!"
    "Я радовался как маленький ребёнок. Даже не смотря на то, что я убил это животное. Я чувствовал победу, заслуженную тяжким трудом победу"
    me "Ред! Ред! Можешь выходить, у меня получилось одолеть волка! Ура!"
    "Из-за холма показался Ред, выглядивший обрадованным не меньше меня"
    show Red at center with dissolve
    "Старик подбежал ко мне, обнял и начал рассматривать мою порванную одежду"
    red "Ну, я и не сомневался в тебе, [me], ты отлично справился. Не без царапин конечно, но это поправимо"
    me "Да, нужно будет перевязать раны. Но я думаю, тут ничего серьёзного. Какие-то лекарства же есть?"
    red "Найдём в таверне, всё же вернёмся туда. Кстати, время уже ближе к полудню, пора бы перекусить!"
    me "Не могу с тобой не согласиться. Эти тренировки оказались весьма выматывающими и стрессовыми"
    red "Тогда давай зря времени не терять. Суй свой меч обратно в ножны, и пошли скорее!"
    "Так мы вместе и направились обратно по тропинке сторону таверны, предвкушая, как отпразднуем мою первую победу за старым добрым дубовым столом"
    scene bg guesthouse1 with fade
    show Host at left
    show Red at center
    host "О, вы вернулись. Вы не ранены, кажется, будто на вас целая стая волков напала! Что же случилось?"
    me "Не поверите, если скажу. Можно что-нибудь поесть и лекарств? Вот пара монет, надеюсь хватит"
    host "Хорошо, сейчас принесу. Вы пока располагайтесь вон за тем столиком, я постараюсь сделать всё как можно скорее"
    hide Host with moveinleft
    red "[me], ты знаешь, как выглядят лекарства не смотря на потерю памяти?"
    me "Да... Я почему-то помню очень много несвязных вещей. Но практически ничего о себе. Лекарства же в виде зелий?"
    red "Не считая бинтов, да. Почти все лекарственные препараты обладают мгновенным эффектом и представляют собой флаконы с жидкостью"
    red "Их изготовлением занимаются алхимики, обычно учившиеся в Мариэне, южном королевстве. А ты наверное и про магию слышал?"
    me "Совсем чуть-чуть. Это вроде особые приёмы, позволяющие концентрировать энергию мира внутри своего тела в качестве катализатора?"
    red "Типо того, я сам не маг, так что в подробности вдаваться не буду. Просто хотел убедиться, что ты хоть немного разбираешься в происходящем"
    "Магия, алхимия. Откуда я вообще знал про них? Неужели я жил в деревне магов? Их же вроде нет в Луфтене"
    me "Ред, а далеко отсюда те деревни, которые мы хотели осмотреть. Ты сказал, что их три, и они находятся по пути в столицу, так?"
    red "Может и по пути. Во всяком случае, мы успеем добраться до одной из них за пару часов быстрой хотьбы, ха-ха"
    me "После вчерашнего от одной мысли протопать дюжину километров на голодный желудок дурно становится. Кстати, еда скоро будет, есть охота"
    show Host at left with moveinleft
    host "Я нашёл только маленькие лечебные зелья и моток бинтов. Еду уже поставил в котёл готовиться. Я решил сделать вам фасолевый суп"
    red "Сойдёт, давай всё это сюда, сейчас будем парня лечить"
    "Ред дал мне глотнуть красноватой жидкости из колбы. Сначала я почувствовал только жжение в горле, но потом заметил, как мои раны начали сами собой затягиваться"
    red "Сюда наложим бинт... Тут уже вроде всё нормально. Так, смотри, всё готово!"
    "Я глянул в запылённое окно и с трудом разглядел себя с бинтом через плечо"
    me "Ну, выгляжу вполне не плохо, мне кажется. Лучше чем до этого, по крайней мере"
    host "Я принёс вам еду, вот, наслаждайтесь"
    "Хозяин поставил две миски с супом на стол, а затем пошёл к выходу, ожидая каких-либо новых гостей"
    me "Вкуснятина, извини, Ред, но это намного лучше твоих сухпайков"
    red "Да я и не спорю, ты наслаждайся, пока можешь. Деньги-то у нас кончаются, нужно искать квесты уже"
    "Да, квесты... Со вчерашнего дня многое поменялось. Теперь для меня это уже не что-то нереальное. Быть может, я бы смог и ещё одного такого волка убить"
    "Надеюсь, в деревне мы их сможем найти. Кто знает, сколько времени нам предстоит ходить по поселениям в поисках моего бывшего дома, если он конечно остался"
    "Мы доели суп и ещё раз проверили наличие всех наших вещей в сумках. Ред мне даже дал небольшой мешок для хранения будущих припасов"
    host "Уже уходите, я прав?"
    me "Да, нам нужно двигаться дальше. Мне с Редом предстоит непростой путь, так что хорошо бы пойти поскорее и успеть до темноты"
    host "Понимаю. Что же, счастливого вам пути. Спасибо, что зашли ко мне в таверну, хоть и на один день. Знайте, я всегда рад своим гостям"
    red "И вам всего хорошего, быть может увидимся ещё, если живы будем"
    hide Host
    hide Red
    scene bg field with fade
    "Мы вышли из таверны и направились дальше по главной дороге. По пути я старался не расспрашивать Реда, который почему-то снова погрузился в раздумья"
    "Пейзажи, честно говоря, уже выглядели скучноватыми. Очень странно, что в этих краях мы так и не встретили ни единого человека, будто все они сквозь землю провалились"
    show Red at center with dissolve
    me "Ред, а где все люди? Мне кажется, будто здесь нет ни единой души кроме нас"
    red "Да, на дорогах сейчас действительно людей не много. Но ты пойми, мы же на окраине королевства! Конечно, ни один дурак сюда просто так не поедет"
    red "Кроме меня и тебя. Кстати, надо свериться с картой, не сбились ли мы случайно с пути"
    me "Как тут сбиться, одна дорога же, лес с одной стороны, горы с другой"
    "Пройдя ещё несколько километров молча, мы вышли на тройную развилку. Две дороги уходили куда-то в сторону гор, а другая вела в лес"
    me "Куда теперь? Тут три дороги, все примерно одинаковые"
    red "И без тебя вижу. Смотри, вот та, которая ведёт в лес и та, которая уходит вправо, ведут в две деревни. Третья же уходит далеко к третьей, а потом и в столицу"
    me "Предлагаешь мне выбрать, в какую сторону пойти?"
    red "Да, к тому же мы всё равно с большой вероятностью обратно сюда вернёмся, так что решай: деревня Полого Холма или деревня Красного дуба?"
    red "Есть ещё деревня Криа, но её оставим напоследок, она отсюда далековато"
    me "Мда, ну и названия. Ну ладно, сейчас подумаю, хм..."
    define lightning_strike_claimed = False

label three_villages_road:
    scene bg field with fade
    show Red
    menu:
        "Деревня Полого Холма" if not expl_choice1:
            if expl_choice2:
                me "Чтож, теперь придётся отправится в деревню Полого Холма"
            else:
                me "Начнём наше путешествие с деревни Полого Холма!"
            jump hollow_hill_village
        "Деревня Красного Дуба" if not expl_choice2:
            if expl_choice1:
                me "Чтож, теперь придётся отправится в деревню Красного Дуба"
            else:
                me "Начнём наше путешествие с деревни Красного Дуба!"
            jump red_oak_village
        "Деревня Криа":
            if expl_choice1 and expl_choice2:
                jump kria_village
            else:
                me "Может всё-таки отправимся в деревню Криа? Я вижу, там и дорога поровнее, да и по пути нам..."
                red "Ага, сейчас! А если мы там ничего не найдём? Предложишь назад возвращаться? Ну уж нет, я такой прогулки не выдержу"
                me "Ну ладно-ладно, придумаю что-нибудь ещё. И вообще, сам же сказал выбирать, не надо ругаться"
                jump three_villages_road

label hollow_hill_village:
    $ expl_choice1 = True
    $ chapter = 2
    $ stage = "Деревня Полого холма"
    $ save_name = "Глава " + str(chapter) + ". " + stage

    red "Хорошо, он отсюда сравнительно недалеко находится. Я думаю до вечера уже будем там"
    me "Ред, а ты там уже был? Неужели ты успел обойти все эти деревни Луфтена?"
    red "Ха, да нет. Просто я достаточно хорошо знаю местность. К тому же по карте почти всё видно"
    red "Много старых дорог, разве. Это плохо, большинство давно поросли травой и опасны для путешественников"
    hide Red with dissolve
    "Дорога постепенно стала сворачивать в лес. Некогда длинная протоптанная повозками дорога сменилась на узкую тропу с еле заметными следами ботинок"
    "Мы прошли мимо одинокой замшелой вывески, а которой полустёртой чёрной краской было написано: \"Деревня Полого Холма\""
    scene bg forest_village with dissolve
    "Уже через пару десятков метров моему взору открылась маленькая деревушка, расположенная между огромными елями и соснами, закрывавшими небо своими ветвями"
    "Само поселение, как и следовало ожидать, располагалось на небольшм холме и было окружено частоколом из старых стволов деревьев"
    me "Странно, а где все люди? Ред, ты же сказал, что в деревнях их как раз таки много"
    show Red at left
    red "Понятия не имею, если честно. Давай пройдём в деревню, там посмотрим. Не могли же они просто так испариться"
    "Не успели мы войти внутрь деревни, как вдруг, как будто из ниоткуда появился человек с палицей в руках"
    show Ted_Gensin with fade
    "Мужчина" "Кто вы такие? Зачем пришли в эту деревню, вам здесь не место!"
    red "Мы путешественники, пришли в эту деревню, чтобы поискать работу и разузнать кое-о-чём. А вы собственно кто?"
    tedg "Я - Тед Гензин, стражник этой деревни. По воле старейшины, я охраняю это место от посторонних. Так что убирайтесь прочь, пока не поздно!"
    me "Подождите, сэр Гензин! Мы не желаем никому зла, видите, нас всего двое а из оружия у нас только вот этот обыкновенный меч"
    tedg "И что с того? Мне до этого вообще какое дело? Сказано же, убирайтесь, не заставляйте меня применить силу"
    "Здесь явно что-то не так. Поблизости нет ни души, внутри не слышно голосов. Что же скрывает этот человек?"
    me "Почему вы никого не пускаете в деревню? Где вообще все жители? Там остался кто-то живой, или вы всех убили?"
    tedg "Что... Нет, я же сказал, это приказ старейшины. Мне было велено не пускать внутрь никого, а также следить за тем, чтобы все жители сидели в домах..."
    "Возникло неловкое молчание. Гензин будто подбирал слова, чтобы что-то сказать и выглядел весьма расстеряным"
    tedg "Слушайте. Не думайте обо мне ничего плохого. Просто за последний месяц из деревни пропало уже семь человек по неизвестной никому причине"
    tedg "Старейшина объявил коменданский час, пока ситуация не прояснится. Я сам не рад тому, что обязан прогонять путников"
    me "Вот оно как... А мы не могли бы помочь вам? Мы же путешественники, нам нужны задания. Разве это не тот случай, когда стоит обратиться за помощью?"
    red "Подожди, [me], ты же даже не знаешь, что случилось! Мы можем влезть в такую передрягу, откуда вряд ли выберемся"
    me "Ну и что? Если мы разузнаем причину пропажи жителей, то это возможно приведёт нас к разгадке моей тайны. Мы же за этим сюда пришли!"
    "Ред промолчал. По его лицу было видно, что он нехотя согласился с моими словами"
    me "Господин Гензин, расскажите всё, что знаете, и мы поможем вам, я обещаю. Для меня очень важно поговорить с жителями деревни, и я ради этого готов на всё"
    "Гензин нахмурился. Неудивительно, моя просьба шла практически вразрез с приказом старейшин. Но моё предложение было весьма заманчиво"
    tedg "Что вы хотите взамен?"
    me "Только поговорить с местными, ничего более. Это единственное моё условие"
    tedg "Ладно, по рукам. Но только после того, как вы расскажите мне причину исчезновения людей. До этого момента разрешено говорить только со мной. Внутрь деревни заходить нельзя"
    me "Отлично! Мы согласны. Не могли бы вы рассказать о том, как же всё это произошло. Нам нужны хоть какие-нибудь зацепки"
    tedg "Хорошо, я скажу всё, что знаю.\nМесяц назад начали пропадать жители деревни. Сначала это была мать с сыном, они пошли к ручью вечером и не вернулись"
    tedg "Где-то через неделю после этого пропал обычный сельчанин. Последний раз его видел владелец трактира, мужчина шёл мимо его дома"
    tedg "На их поиски была собрана небольшая группа из наших охотников. В первые два дня они ничего не нашли, а на третий и их след простыл"
    tedg "И вот недавно ещё пропал наш лесоруб. В деревне закончились дрова, и он вызвался нарубить их хотя бы на несколько дней. и его теперь нет"
    tedg "Так как почти все люди пропали именно за пределами селения, на совете было решено запретить выход хотя бы на пару недель. Считалось, что это поможет прояснить ситуацию"
    tedg "Прошло уже три дня, и пока что все живы. Но что же произошло со всеми пропавшими так и остаётся загадкой. Это всё, что мне известно"
    me "Хорошо, можно уточнить тогда ещё какое-какие детали, это может быть нам полезно"
    tedg "Ну валяй, если знаю, отвечу. Только если бы всё так просто было, такое количество людей не пропало"
label ted_gensin_ask:
    menu:
        "Где были охотники?":
            $ ask_counter1 = True
            me "Не могли бы вы рассказать, где были охотники? Как вы узнали, что пропали они именно на третий день поисков?"
            tedg "Я точно не знаю, где они были, простите. Обычно они уходили днём и до глубокой ночи были заняты поисками. Возвращались ближе к утру, чтобы выспаться"
            tedg "Так было в первые два дня. На третий о них не было ни слуху. Мы уже боялись посылать кого-то ещё в лес"
            jump ted_gensin_ask

        "Где находится ручей?":
            $ ask_counter2 = True
            me "В рассказе о пропавшей матери и её сыне вы упоминали ручей. Он отсюда недалеко находится, вы там часто бывали?"
            tedg "Да, этот ручей прямо за соседним от деревни холмом. Метров 400, полагаю. Я бы показал лично, но пост покидать не могу"
            tedg "Там мы всегда набирали воду. Пока что в бочках ещё остались запасы, но боюсь надолго их не хватит. Рано или поздно кому-то придётся покинуть селение"
            jump ted_gensin_ask

        "Что известно о пропавшем сельчанине?":
            $ ask_counter3 = True
            me "Куда шёл тот мужчина, которого видел хозяин трактира? Когда его видели в последний раз?"
            tedg "Вроде у одного из его друзей был день рождения, вот они и собрались праздновать. Попили, ну и по домам разошлись. Тогда наверное он и шёл в сторону своего дома"
            me "Он мог быть пьян? Хозяин этого не упоминал в своём рассказе?"
            tedg "Кто его знает, наверное, раз праздник был. Хозяин только краем глаза его видел, так что рассказать ничего дельного больше не мог"
            jump ted_gensin_ask

        "Когда и где пропал лесоруб?":
            $ ask_counter4 = True
            me "Одним из пропавших жителей был лесоруб. Когда это случилось? Куда он обычно ходит, чтобы нарубить деревья?"
            tedg "Случилось это... Не знаю, наверное ближе к вечеру, когда печи топят, чтоб светлее было. Дров не оказалось, он и пошёл рубить"
            tedg "Тут мест много, лес же чёрт возьми. Честно, хер его знает, где именно он был в тот день. Думаю, он бы не стал отходить от деревни слишком далеко"
            jump ted_gensin_ask

        "Закончить разговор" if ask_counter1 and ask_counter2 and ask_counter3 and ask_counter4:
            me "Думаю, этой информации нам будет достаточно. Спасибо, что уделили нам время, теперь мы можем приступать к поискам"
            $ ask_counter1 = False
            $ ask_counter2 = False
            $ ask_counter3 = False
            $ ask_counter4 = False
    tedg "Не за что. Если узнаете, что с ними произошло или найдёте кого - сразу же возвращайтесь ко мне. я стою на посту до самого утра"
    me "Хорошо, обязательно так и сделаем. Мы пока что осмотрим округу, как я понял, все пропавшие не уходили слишком далеко от деревни"
    hide Ted_Gensin with dissolve
    show Red at center with moveinleft
    red "[me], у тебя есть идеи? Я пока что мало чего узнал из полученной от Гензина информации"
    me "На самом деле есть некоторые зацепки. К примеру, тебе не кажется странным, что все случаи произошли именно ночью?"
    red "Ночью... Разве это так очевидно? Мне казалось, что тут нет никакой связи. Как ты сделал такой вывод?"
    me "Мы знаем, что лесоруб пропал вечером, когда пошёл нарубить дров для топки печи. Также известно, что охотники бродили по лесу до утра"
    me "Сельчанин, отмечавший день рождения друга, небось тоже вечером возвращался. Он был скорее всего пьяный, я не удивлюсь, если он ненароком просто свернул не в ту сторону и вышел за пределы деревни"
    me "Остаётся матерь с ребёнком. Они тоже могли уже в темноте отправиться, ведь они первые пропали и не знали об опасности. Нужно будет проверить тот ручей, о котором говорил Гензин"
    red "Хм, звучит очень даже убедительно. Но что же могло с ними со всеми стать? У лесоруба как минимум был топор, а охотники вообще вполне могли иметь при себе арбалеты и мечи"
    me "Это нам и предстоит узнать. Предлагаю осмотреть для начала ручей. Охотники думаю тоже первым делом направились туда"
    red "А ты не боишься, что это окажется какой-нибудь монстр, и он нападёт на нас? Что же тогда будем делать?"
    me "Боюсь. Но выбора у нас нет. Придётся драться, убежать вряд ли получиться, тем более, ни в коем случае нельзя приводить его к деревне"
    me "Если это окажется банда бандитов, думаю, у меня получится что-нибудь придумать. Денег у нас конечно нет, но вот голова пока на плечах"
    red "Ох, и влипли мы в передрягу. Как бы как раз без головы и не остаться. Ну, раз решились, то давай, поищём тот злополучный ручей"
    hide Red with dissolve
    scene bg forest_river with dissolve
    "Мы взобрались на соседний холм, как нам и сказал Гензин. Затем прошли ещё несколько сотен метров, пока не вышли из под сосен к тому самому ручью"
    "Я подошёл к воде и зачерпнул немного рукой. Это было холодная, свежая, кристально чистая родниковая вода"
    "Я достал вляжку, подаренную Редом ещё в таверне перед нашим уходом, и окунул её в ручей"
    show Red at right with moveinright
    red "Здесь так тихо. Такое чувство, будто здесь никогда не может случится ничего плохого"
    me "Мне тоже так кажется. Но факт того, что пропало семь человек, остаётся. Давай пройдём вдоль этого берега и поищем улики"
    "Ред и я прошли параллелельно ручью сначала против течения. Через метров двести мы напоролись на заросли и решили, что жители вряд ли ходили в эту сторону"
    red "Эй, [me], смотри, что я нашёл! Совсем недалеко от места, где мы вышли к ручью, подходи быстрее!"
    scene bg black with fade
    "Я подбежал в Реду и вдруг встал как ошарашенный. На земле, прямо там, где стоял старик, лежал окровавленный топор с засохшими следами по всей поверхности"
    scene bg forest_river with fade
    show Red at right
    red "Крови уже несколько дней. Видимо, это произошло в тот день, когда лесоруб пропал. Что же с ним стало?"
    me "Ты можешь определить, чья это кровь? Человека? Того самого лесоруба или кого-то ещё?"
    red "Дай-ка посмотреть... Нет, это не человеческая кровь. Похожа... Нет, не знаю, явно какой-то монстр, но сходу сказать не могу"
    red "Многих монстров можно определить по их крови. Но если ей несколько дней и она несвежая, то это становится очень трудно, особенно в полевых условиях"
    me "Что же получается, лесоруб дрался с монстром и нанёс ему ранение? Тогда где же следы от ранения?"
    red "Топор находился под деревьями и хорошо сохранился. Но, как ты помнишь, вчера ночью шёл дождь, так что возможно почти всё было смыть водой. К тому же... Тут рядом есть ручей"
    me "Хочешь сказать, что монстр мог уйти со своей добычей по ту сторону водоёма, смыв часть крови?"
    red "Очень вероятно. Нужно перейти через ручей и посмотреть, не найдём ли мы ещё улик"
    scene bg forest_river with fade
    "Мы прошли по прямой до берега. Не придумав ничего лучшего, я просто прыгнул в воду и прошёл на другую сторону. Ред последовал за мной"
    me "Брр, холодно то как. Хорошо хоть ещё лето, так что в лесу достаточно тепло. Иначе тут же слёг бы от простуды"
    "Я осмотрел противоположный берег на следы крови и какие-то другие вещи, оставленные пропавшими жителями, но ничего не нашёл"
    me "Может они все уже убиты, а монстр давно сбежал? Тогда мы зря тратим время на поиск следов, всё равно прошло несколько дней и он может быть уже в десятках километров от деревни..."
    show Red at left with dissolve
    red "Нет, они так не поступают. Раз  он смог найти добычу у ручья несколько раз, он обязательно вернётся сюда снова. Скорее всего, он даже поселился где-то поблизости, чтобы чаще проверять, не пришла ли очередная добыча"
    me "Ты так говоришь, будто уже знаешь, с кем мы имеем дело. Сам же сказал, что по крови определить нельзя. Вдруг это такой монстр, у которого нет постоянного места обитания"
    red "Да, не все монстры такие. Но кроме крови есть и другие способы понять, кого мы ищем. Ты не заметил, что на этой стороне у деревьем много поломанных веток?"
    me "Хм, да? Я как-то не обратил внимание. Это же мог быть и простой ветер во время дождя, или ещё что угодно"
    red "Ветер во время дождя ломает ветки только в трёх метрах от земли? Ну-ну, так я тебе и поверил. Смотри в оба, мне кажется, мы нашли по какой дороге ходит это чудище"
    me "Три метра? Кто это может быть? медведь?"
    red "Если честно, нет. Но я хочу убедиться в своей теории. Давай пройдём по этой тропе и узнаем, есть ли кто там сейчас"
    scene bg forest1 with fade
    "Я шёл за Редом вдоль деревьев, к которых были отломаны ветки. Интересно, что места, где деревья стояли слишком близко друг другу, были почти нетронуты"
    "Вдруг Ред остановился и спрятался за дерево. Я последовал его примеру и встал рядом с ним"
    show Red at left
    me "Ред, что случилось, ты что-то увидел? Кто там, монстр?"
    red "Тише. Пока нет, но там видны следы его ног. Он где-то рядом, нужно быть предельно аккуратными, так как если он нас заметит, боюсь нас настигнет участь селян"
    me "Что же ты предлагаешь делать? Вернуться в деревню и рассказать об этом? Можно собрать отряд и уничтожить его сообща"
    red "А толку возвращаться? Охотников там уже не осталось, а Гензин сказал, что не будет помогать нам в поисках. К тому же, к моменту, как мы сюда придём, уже наступит ночь и он снова пойдет искать жертв..."
    me "Стой, ночь! Он же действует по ночам, мы это выяснили. А спит он тогда когда? Не может же монстр целый день бродить по лесу"
    red "Верно... То есть ты хочешь сказать, что он сейчас спит и не заметит нашего присутствия?"
    me "Я так считаю! Нужно попробовать пробраться поближе... Только я не знаю, где он. Ред, давай ты подождёшь здесь и проследишь, чтобы никто не зашёл со спины, а я пойду по следам. По рукам?"
    red "По рукам... Только, будь аккуратен. Если у тебя не получится убить его, пока он спит, тебе придётся драться с ним один на один"
    me "Я понимаю, но другого выбора нет. Я постараюсь прикончить его одним ударом, в случае чего - не вини себя, Ред"
    red "Мггх, ладно, иди. Но прежде я дам тебе совет: если он проснётся, следи внимательно за его атаками. От особо сильных попробуй защититься, не несись сломя голову"
    red "Это не волки и не бандиты, малейшая оплошность может оказаться фатальной... Поэтому, будь аккуратнее, [me]"
    hide Red with dissolve
    "Выйдя из-за дерева, я аккуратно пошёл по следам, стараясь не издавать лишнего шума. Ред остался сторожить путь, по которому мы пришли"
    "Пройдя несколько десятков метров по ещё свежим, видимо вчерашним, следам и периодически прячась за стволами деревьев, я вышел на поляну"
    "Увиденное заставило меня снова пошатнуться, как когда я нашёл тот залитый кровью топор. Только на этот раз это чувство было в несколько раз сильнее"
    "На поляне, среди горы окровавленных трупов людей и животных лежало огромное существо, храпя и источая от себя зловонный аромат"
    scene bg black with fade
    "Это был тролль. Его тело было изрезано, чувствовались среды борьбы. Видимо, вокруг валялись останки тех самых жителей, ушедших из селения"
    "Чувство гнева, расстрелянности и страха наполнили всё моё тело. Кажется, будто я забыл, зачем здесь оказался. Мысли то и дело мелькали у меня в голове, я думал, что же мне теперь делать"
    "Неловко шагая, я подошёл к этому к ногам этого огромного существа, достал свой, уже казалось крохотный, меч. И приготовился нанести удар"

    define health = 300
    image troll = "images/troll.png"
    menu:
        "подойти ближе и нанести удар в голову":
            "Нужно подойти поближе к его голове. Пока он спит, я могу прикончить его одним ударом, если пробью череп"
            "Я аккуратно прошагал по останкам его трапезы. Остановившись около его головы, я занёс меч, чтобы нанять фатальный удар..."
            scene bg forest1 with fade
            show troll at center with moveinbottom
            "Вдруг тролль просыпается и тут же откидывает меня от себя! Я врезаюсь в дерево и падаю на сырую после дождя землю"
            "Огромное существо встаёт на ноги и берёт в руки дубину, сделанную из поваленного дерева. Выйдя из кратковременного шока, я, опираясь на свой меч, встаю и готовлюсь к бою"
        "ударить по ноге тролля и отпрыгнуть":
            $ health = 250
            me "Получи тварь! Вот тебе за всех тех, кого ты убил без капли жалости и сострадания!"
            "Я втыкаю меч в левую ногу чудовища а затем резким движением выдёргиваю его из твёрдой плоти. Кровь брызнула, и полилась струёй"
            "Тролль получает 50 ед. урона"
            scene bg forest1 with fade
            show troll at center with moveinbottom
            "Тролль дёрнулся, и внезапно завыл протяжным криком. Оперевшись на руки, он начал медленно вставать. Я отпрыгнул подальше на несколько метров и встал наготове"
            "Хромая, он взял свою дубину, сделанную, по видимому из старого поваленного дерева, а затем кинул взгляд на меня"
            "Я ни заметил в его глазах ничего человечного. Только ярость и животный гнев за то, что я нанёс ему тот удар"
            "Снова заревев и ударив дубиной об землю, монстр начал медленно подходить ко мне"

    $ renpy.block_rollback()

    define troll = None

    $ Player = player(level, xp, std_player_update)
    if lightning_strike_claimed:
        $ Player.attacks.append(attack("Молниеносный удар", lightning_attack, value = Player.max_damage, cost = 2))

    $ attacks = []
    $ attacks.append(attack("Тролль ударяет дубиной по вам!", std_base_attack, 20, 0))
    $ attacks.append(attack("Тролль кидает в вас огромный валун!", std_base_attack, 20, 0))
    $ attacks.append(attack("Тролль издаёт боевой рык и прыгает прямо на вас!", std_base_attack, 15, 0))
    $ attacks.append(attack("Тролль поднимает дубину над своей\nголовой и медленно наступает", std_block_attack, 0, 0))
    $ attacks.append(attack("Тролль со всей силы ударяет своей дубиной!", std_base_attack, 50, 0))

    $ troll = enemy("тролль", 500, std_enemy_update, std_enemy_rand)
    $ troll.health = health
    $ troll.attacks = attacks

    $ Log = log(std_win_check, std_lose_check, std_log_update, "Началась битва с троллем!")

    call screen fight_screen(Log, Player, troll)
    hide troll with fade

    $ newLv = Player.add_xp(250)
    $ level = Player.level
    $ xp += 250

    $ renpy.block_rollback()

    "Вы получаете 250 ед. опыта!"
    if newLv:
        "Ваш уровень повышен до [level]!"
    "Это... Это было очень нелегко. Я еле стою на ногах после битвы с этим чудищем... Нужно найти Реда..."
    "Я медленно начал идти в обратную сторону. Ноги почти поднимались, я чувствовал, что мои силы полностью иссякли. Хотелось спать"
    scene bg black with fade
    "Потеряв почти все силы, я упал у дерева и потерял сознание. Весь мир погрузился во тьму"
    "Голос: " "Эй, [me], вставай! Ну же, давай!"
    "Чей это голос... Что со мной... Где я нахожусь... "
    "Голос" "Тащите сюда ведро с водой, помогите ему очухаться!"
    "Что... Вода?! Нет!"
    scene bg forest_village with dissolve
    show Red at center
    show Ted_Gensin at left
    "Я резко вскочил, ополоснутый ледяной водой из ведра. Весь мокрый, я сидел на земле, а вокруг меня стоял Ред и Гензин"
    me "Где я нахожусь? Ред? Сэр Гензин... А тролль, он?.."
    red "Всё хорошо, парень, ты справился, он уже мёртв"
    tedg "Да, Ред нашёл тебя в лесу рядом с тушей этого монстра. К сожалению, людей к тому моменту уже не осталось, но во всяком случае жертв более не будет"
    tedg "Вы с Редом очень помогли всей деревне, поэтому, как и договаривались, ты имеешь полное право пройти внутрь. К тому же, старейшина выдал тебе в награду это"
    "Гензин протянул небольшой мешочек со звенящими монетами. Я сначала было хотел отказаться, но, увидя пламенный взгляд Реда, решил не рисковать"
    me "Спасибо. Так все уже знают, что я одолел тролля и в лесу снова более-менее спокойно?"
    tedg "Да, я думаю теперь в нашей деревне тебе поможет любой. Единственное, многие оплакивают погибших, так что будь аккуратнее"
    tedg "Ах да, и ещё кое-что. Старейшина просил передать грамоту, вы, путешественники, вроде особо цените их, а ты как никак выполнил задание по убийству монстра"
    "Гензин протянул бумагу с красной печатью мне в руки. Я аккуратно взял её, и хотел было открыть, но в этот момент Ред толкнул меня вбок"
    me "Да, спасибо. Вообще мне хотелось бы найти ответы как можно скорее, поэтому я отправлюсь в деревню прямо сейчас, если вы не возражаете"
    tedg "Не возражаю, только вот о чём ты собственно хотел просить? В чём твоя цель, ради которой ты был готов даже пожертвовать своей жизнью?"
    me "Я хочу узнать своё прошлое. Ред нашёл меня у дороги, когда я полностью потерял память. До сих пор я ничего не вспомнил, но есть вероятность, что кто-нибудь здесь знает обо мне"
    "Гензин промолчал. Хотя мне показалось, что он всё же что-то хотел сказать, я не стал растягивать время и пошёл в деревню вместе с Редом"
    scene bg forest_village with fade
    "До самой ночи мы расспрашивали местных о том, не  знакомы ли они со мной или хотя бы просто слышали обо мне"
    "Некоторые в ответ качали головой, другие пытались меня вспомнить, но всё было без толку. В этом месте я никогда не был, а значит, делать здесь больше нечего"
    "Поняв это, я почему-то даже немного приуныл. Остановившись на полянке, я посмотрел на небо и о чём-то задумался"
    show Red at center with dissolve
    red "Эй, [me], ты чего! Не расстраивайся, что не смог здесь никого найти. Я понимаю, тебе трудно, но нужно идти дальше. К тому же, у нас снова хватает денег на еду"
    me "Это конечно здорово... Но что будет, если мы так не найдём мою семью? Что же тогда делать, куда мне одному идти?"
    "Ред стоял в раздумьях рядом со мной. Я понимал, что заставляю его переживать за меня, но ничего не мог с этим поделать. Или же попросту не хотел"
    red "Если хочешь, можешь отправиться в столицу со мной. Вообще, эти деревни практически по пути, так что ничего страшного, что мы по ним ходим"
    red "Ты хорошо владеешь мечом, я хорошо владею имеющимися деньгами. Вместе мы сможем покорить этот мир, ха-ха!"
    "Предложение Реда вызвало у меня улыбку на лице. Я немного повеселел от его добрых слов и был рад тому, что он готов и дальше помогать мне"
    me "Хорошо, Ред, я согласен. Если мы всё же не найдём моих родных, я обязательно присоединюсь к тебе. А теперь, нам пора в путь"
    red "По рукам! Впереди нас ждёт следующая деревня, кто знает, что мы там встретим? Может заработаем ещё больше деньжат!"
    me "Ну ты всё о деньгах... Я не смогу победить ещё одного тролля, между прочим. Тем более, зная, что после этого буду облит ледяной водой"
    "Ред рассмеялся и наш маленький отряд снова отправился в путь. Плутая по тропам густого хвойного леса, спустя где-то час мы кое-как добрались до того самого перекрёстка"
    red "Я бы был не против наконец отдохнуть. Ещё и есть ох как охота... Поискать бы в деревне какую-нибудь таверну. Ноги совсем устали"
    me "Да, я за. Ну что же, в таком случае, давай отправимся в селение под названием..."

    jump three_villages_road

label red_oak_village:
    $ stage = "Деревня Красного Дуба"
    $ chapter = 2
    $ save_name = "Глава " + str(chapter) + ". " + stage
    $ expl_choice2 = True

    red "Деревня Красного Дуба находится недалеко от северного горного каскада и ограждено от океана, что весьма удобно"
    red "Большинство монстров, живущих близ воды не могут попасть внутрь, так что вряд ли мы наткнёмся там на каких-либо опасных врагов"
    me "Обнадёживающе. Я надеюсь, что удача будет к нам благосклонна и мы найдём моих... родных?"
    red "Я тоже. Идти туда три часа, так что самый лучший вариант первым делом зайти в таверну, можно расспросить местных прямо там"
    hide Red with fade
    "Я пошёл за Редом по дороге в сторону туманных скал, нависших над горизонтом. Дорога была извилистая, приходилось то и дело спускаться вниз, а потом опять подниматься вверх"
    me "Ред, ты мне помню про Фандер и Мариэн рассказывал, я прав?"
    red "Ну было дело... А ты это к чему?"
    me "Да так. Интересно стало, как другие королевства выглядят. Луфтен я смотрю достаточно миролюбивая страна, тут даже монстров почти нет"
    red "Да, всё так и есть. Это самое спокойное место на всём материке. Можно даже сказать, что тебе очень повезло, что ты оказался именно здесь, а не в каком-нибудь Фандере"
    me "А что с Фандером? Я знаю, он находится на северо-востоке. Но не ты, ни кто-либо ещё о нём мне не рассказывал. Там же тоже живут люди?"
    red "Живут... Но это совершенно другая страна со своими законами и порядками. Не смотря на то, что это самое маленькое из трёх государств, Фандер обладает колоссальной боевой мощью"
    red "Первый его город был построен 789 лет назад и до сих пор существует как столица королевства. Люди в этой стране в основном занимаются кузнечным делом или работают в качестве наёмников"
    red "Торговцев там тоже немало, но только в центральных районах. Большая часть территории покрыта непроходимыми хвойными лесами или скалистыми заснеженными горами"
    red "Добраться от границы до ближайшего населённого пункта уже большая проблема, а оттуда же надо будет ещё километров 40 сквозь лес пробираться. Дорог нормальных почти нет"
    red "Помимо всего прочего, именно там обитают самые сильные монстры, так как место ближе всех к Великому Хребту, много лет служившему обителью всякой нечисти"
    red "Про правителя тоже можно сказать немало. Его имя Имер IV и он стал широко известен во всём Инзеле из-за своей внешней политики. Даже получил прозвище \"Всадник-Одиночка\""
    red "Не желая сотрудничать с другими королевствами, он огородился от всех стенами из воинов и камня, а также установил строжайший контроль на двух Вратах, ведущих в Луфтен и Мариэн"
    red "Мало путешественников отправляются туда, многие погибают от рук монстров или становятся жертвами распущенной стражи. В последнее время много народу наоборот старается эмигрировать из страны"
    "Рассказ Реда заставил меня задуматься о том, сколько всего я ещё не знаю. Ведь я до сих пор даже не видел крупный город, а если представить, что есть целых три огромных державы..."
    "Даже жутко становится. И ещё больше чувствуется, что я всего лишь маленькая песчинка в этом огромном мире"
    "Мы шли уже несколько часов. Постепенно погода становилась всё холоднее и я начал даже постепенно замерзать"
    me "Бррр... Ред, что так холодно, руки холодные аж жуть! Мы точно всё ещё в Луфтене?"
    red "Да. Конечности мёрзнут потому, что мы постепенно поднимаемся в горы и к тому же идём на север. Конечно же здесь погода будет холоднее"
    red "Ничего, осталось недолго, и скоро мы будем на месте. Деревня Красного Дуба уже совсем рядом"
    "Мы поднялись на поросший бурьяном холм, и мне открылся потрясающий и в тоже время мрачный вид"
    scene bg mountain_village with dissolve
    "Прямо близ отвесного склона, между хвойными тёмными деревнями, на поляне располагалась деревня Красного Дуба. Ещё сверху было видно, как крестьяне переносят грузы, рубят деревья и строят очередное здание для хранения припасов"
    "Я медленно начал спускаться с холма в сторону поселения. Мне было чрезвычайно интересно распросить местных обо всех вещах, которые вызывали у меня вопросы"
    "Спрыгнув с уступа, я подбежал к ближайшему рабочему, таскавшему брёвна на склад. Не смотря на то, что на меня уже начали таращиться несколько человек, я окликнул местного"
    show villager with moveinbottom
    me "Извините, сэр, вы не могли бы ответить на пару моих вопросов?"
    "Рабочий остановился и посмотрел на меня косым взглядом, будто оценивая мою внешность. Брови его нахмурились"
    villager "Что тебе надо, парень? Не видишь, я занят, некогда мне на вопросы каких-то проходимцев отвечать"
    me "Подождите! Это очень важно! Пожалуйста, скажите хотя бы у кого можно спросить..."
    villager "В таверну иди, там тебе бармен всё расскажет, если за выпивку заплатишь. А ко мне не лезь. Мне работать надо"
    hide villager with moveinleft
    "Житель пошёл дальше в сторону склада. Прохожие тоже начали постепенно расходится по своим делам. Мда, не такого приёма я ожидал от местных жителей"
    "Мне покалось даже странным, что никто из местных не захотел говорить со мной. Неужели это у них тут такой менталитет? Удивительные люди всё-таки проживают в Инзеле"
    me "Ладно... Таверна значит. Она же где-то рядом находится? Зайду-ка я туда"
    show Red at center with moveinright
    "Ко мне подбежал Ред, запинаясь об упавшие ветки и корни деревьев. Запыхавшись и стараясь прийти в себя после такого быстрого спуска с холма, он прислонился к забору и бросил на меня неодобрительный взгляд"
    red "Ты куда несёшься-то? Мы же и так договорились первым делом в таверну пойти, а ты зачем-то начал к рабочим приставать! У них и без тебя хлопот по горло"
    me "Да понял я, просто хотелось поскорее узнать, не это ли моя родная деревня. Хотя, меня бы тогда узнали уже..."
    red "Всё равно, давай сначала в таверну. Там и поесть можно, и много ценного узнать. Ты поверь, я-то знаю, как в таких местах информацию добывать"
    "Следуя совету Реда, мы прошли по центральной улице к большому двухэтажному зданию с красивой вывеской: \"Таверна Красного Дуба\""
    scene bg guesthouse2 with fade
    "Мы зашли внутрь здания. На самом деле, всё тут выглядело достаточно похоже на то место, где мы впервые остановились с Редом"
    "Неужто все таверны так похожи? Даже хозяин выглядит примерно также, вот тебе и разнообразный мир"
    show Host with dissolve
    show Red at right with fade
    host "Здраствуйте, господа! Как мило, что вы решили зайти к нам в деревню на огонёк! Куда путь держите?"
    red "В Луфтен. По пути мы решили зайти в вашу деревню так сказать, отдохнуть. У вас же есть выпивка?"
    host "Конечно! Любой напиток на ваш выбор. Моя таверна также предоставляет богатый ассортимент самых разных блюд по приемлемым ценам..."
    red "Мы поняли. Можно виски и что-нибудь мясное. Желательно, чтобы готовилось недолго"
    host "Будет сделано! Присаживайтесь за любой стол, в течение получаса всё будет готово"
    hide Host with fade
    "Мы уселись за ближайший стол у окна. Рядом с нами беседовали какие-то мужики, видимо, зашедшие в таверну на обеденный перерыв"
    me "Хозяин выглядит очень гостеприимным. Совсем не так, как тот рабочий с улицы. Может, его нам как раз и спросить?"
    red "Можешь попробовать. Я считаю, что им всем просто деньги нужны, и побольше. Вот и любезничают с каждым встречным, кто удосужился внутрь зайти"
    me "Ну Ред, зачем ты так о людях. Он наверное просто гостям рад, всё таки таверны, как я понял, как раз и сделаны для путешественников"
    red "Тем не менее, постарайся реже задавать вопросы. Особенно, если окажешься в столице. Там много самых разных личностей, и ты никогда не можешь знать, какова будет их ответная реакция"
    me "Принято к сведению. Я просто многое действительно не знаю, и к тому же очень некомфортно всегда полагаться на других. Видимо это всё из-за потери памяти"
    red "Да ничего, я же Ред, я на твоей стороне! Ко мне ты точно всегда можешь обратиться с советом"
    show Host at center with moveinright
    host "Вот ваш виски сэр. Еда пока готовится, но в целом с вас 20 серебряных"
    "Ред нехотя отсыпал из мешочка горстку монет и протянул их хозяину. Я же, не став медлить, решил наконец задать вопрос"
    me "Извините, сэр, не могли бы вы ответить на пару вопросов. Я заплачу ещё пять серебряных, если вы поможете"
    red "Мгхх..."
    host "Конечно, с превеликим удовольствием. Если я что-либо знаю, то обязательно отвечу, господин... Как вас называть?"
    me "[me]. Меня так зовут. Вы не слышали раньше этого имени?"
    host "Сожалению, господин [me], но я не слышал о вас. Вы наверное какой-то известный рыцарь или путешественник, я прав?"
    me "Эм, не думаю. Но ладно, ничего страшного, если вы меня не знаете, я вряд ли был особо известным ранее. Однако, Я бы всё равно хотел, чтобы вы помогли мне"
label host_ask:
    menu:
        "Пропадал ли кто-нибудь из деревни в последнее время?":
            me "Не было ли в деревне случаев, когда кто-то ушёл на юг, и не вернулся? Может быть, стражник или лесоруб?"
            host "Не припомню такого. У нас редко кто пропадает, мы достаточно изолированная от внешнего мира деревня. Даже монстров поблизости нет"
            me "Никто в последнее время не уходил на охоту, к примеру? Он уже вернулся, и много ли времени такие люди проводят в лесу?"
            host "Может пройти день-два. Большинство однако возвращаться в тот же день. К тому же, почти всю деревню я знаю, и могу сказать, что все здесь достаточно сильные и не пропадут зазря"
            $ ask_counter1 = True
            jump host_ask
        "Далеко ли местные уходят от селения работать?":
            me "Местные далеко уходят от деревни? Может, они торгуют с соседними поселениями или ходят в горы искать материалы?"
            host "Вообще, нет, не далеко. Всё необходимое находится прямо вокруг нас: и лес, и вода, и растения. Остаётся только пользоваться этим"
            host "Торговля у нас не задалась. Иногда конечно и торговцы останавливаются проездом, но большиство такие цены выставляет, что любой человек в здравом уме откажется"
            $ ask_counter2 = True
            jump host_ask
        "В округе нет никаких монстров?":
            me "У вас тут необычайно спокойно. Неужели нет ни монстров, ни разбойников?"
            "Возникла неловкая пауза. Хозяин таверны будто намеренно не стал сразу же отвечать на мой вопрос"
            me "Ну так?.."
            host "А? Нет, монстров поблизости нет, чудища у нас не водятся, вокруг всё спокойно. Вы кстати не хотите попить чая, я тут как раз собирался сделать..."
            me "Может быть позже. У меня ещё остались вопросы, на которые я бы хотел услышать ответ"
            $ ask_counter3 = True
            jump host_ask
        "Как часто к вам приходят люди из других деревень?":
            host "Люди... Приходят, иногда. В таверне у меня бывают. Я вот их, как и вас, обслуживаю, они обедают, на ночь комнату берут иногда и на утро уходят"
            host "Долго тут никто не задерживается. Делать особо нечего, старейшины в селе давно нет, задания никто на досках объявлений не размещает. Вот и не никого"
            me "Как это старейшины нет? А кто тогда деревней заправляет? Я думал, что народу нужен своебразный мудрый вождь, который бы направлял всех и конфликты решал"
            host "Ну вот нет его. Умер. Деревня как видите без него держится, люди спокойно себе работают, я тоже не жалуюсь"
            $ ask_counter4 = True
            jump host_ask
        "Кто ещё сейчас находится в деревне?" if ask_counter1 and ask_counter2 and ask_counter3 and ask_counter4:
            $ ask_counter1 = False
            $ ask_counter2 = False
            $ ask_counter3 = False
            $ ask_counter4 = False
            me "Кроме местных, кто ещё сейчас находится в вашей деревне?"
            host "Что вы имеете в виду..."
    "Внезапно входная дверь в таверну распахнулась и на пороге показался человек, окутанный тканью и с капюшоном на голове"
    image rogue1 = "images/rogue1.png"
    show Host at left with moveinleft
    show rogue1 at center with fade
    host "Господин... Извините, простите меня! Я не хотел"
    "Мужчина в капюшоне вошёл в зал. Все посетители тут же начали суетиться и предприняли попытку покинуть здание"
    "Главарь разбойников: " "Никому не двигаться! Если кто из вас отсюда попробует дать дёру, тут же получит меч в спину, поняли?"
    "Главарь разбойников: " "Эй, трактирщик, кто эти двое? Что они забыли в моей деревне, и почему ты их сюда впустил, псина!"
    host "Господин, они пришли..."
    me "Мы путешественники. Мы пришли сюда по одному делу, которое тебя не касается. Хозяин таверны тут не при чём, не трогай его!"
    "Я поднялся со скамейки и встал в нескольких метрах от главаря, придерживая одной рукой меч в ножнах"
    me "Это ведь ты в деревне главный, не так ли? Ты и твои люди заправляют всей этой деревней вместо старейшины?"
    "Я увидел ухмылку на лице этого мужчины. Он стоял совершенно спокойно, ничего не боясь, будто знал, что никто здесь и пальцем не осмелиться двинуть в его присутствии"
    "Главарь разбойников: " "Всё верно, это деревня принадлежит мне. Старейшина уже как несколько лет убит мною и моей бандой, а местные работают на меня"
    "Главарь разбойников: " "От таких как вы мы обычно сразу избавляемся. Вам повезло, что у меня был перерыв и мои ребята не прикончили вас ещё на входе"
    me "Почему тогда нам никто ничего не сказал? Вы так запугали местных, что они даже не будут подавать и знака того, что находятся в заложниках?"
    "Главарь разбойников: " "Ха, ну а ты что думал? Тебе всю правду выложат и помочь попросят? Чудак ты однако, жалко будет такого как ты убивать"
    "Ред, отойди, я разберусь, а ты позаботься о том, чтобы никто более не пострадал!"
    red "Ладно... Только будь аккуратнее, твой противник в этот раз живой человек! Даже не думай сломя голову кидаться в бой, кто знает, какие козыри у него припрятаны"
    me "Я постараюсь справиться. Я не могу дать погибнуть ни тебе, ни кому-либо ещё из мирных жителей!"
    hide Red with moveinright
    hide Host with moveinleft
    "Главарь обнажил свой меч и приготовился к атаке. Я, тоже не медля, встал в защитную стойку, крепко держа свой потрёпанный ржавый меч"
    "Главарь разбойников: " "Не надейся на то, что я тебя пощажу. Сначала сдохнешь ты, а потом и твой старый дружок, хе-хе"
    $ renpy.block_rollback()

    define rogue1 = None

    $ Player = player(level, xp, std_player_update)

    $ attacks = []
    $ attacks.append(attack("Главарь делает подножку и наносит удар ножом!", std_base_attack, 20, 0))
    $ attacks.append(attack("Главарь кидает в вас одним из своих ножей!", std_base_attack, 20, 0))
    $ attacks.append(attack("Главарь атакует мечом, стараясь задеть ваши ноги!", std_base_attack, 15, 0))
    $ attacks.append(attack("Главарь отпрыгивает и встаёт в боевую стойку,\nприготовясь нанести прямой удар мечом", std_block_attack, 0, 0))
    $ attacks.append(attack("Главарь делает резкий выпад вперёд, обнажая свой клинок!", std_base_attack, 50, 0))

    $ rogue1 = enemy("главарь разбойников", 250, std_enemy_update, std_enemy_rand)
    $ rogue1.attacks = attacks

    $ Log = log(std_win_check, std_lose_check, std_log_update, "Битва с главарём разбойников началась!")

    call screen fight_screen(Log, Player, rogue1)

    $ newLv = Player.add_xp(200)
    $ level = Player.level
    $ xp += 200

    $ renpy.block_rollback()

    "Главарь разбойников: " "Невозможно... Как я мог... пасть от руки такого, как ты..."
    hide rogue1 with dissolve
    "вы получаете 200 ед. опыта!"
    if newLv:
        "Ваш уровень повышен до [level]!"
    "Я опустился на пол, закрыв рукой рану на животе. Из неё сочилась свежая красная кровь"
    "Ко мне тут же подбежал Ред, заставил выпить едкое зелье и приказал хозяину таверны сбегать на кухню за какими-то травами"
    scene bg black with dissolve
    red "[me], эй, ты как? Кивни, если понимаешь меня? Ну же давай!"
    me "А... Да, я здесь, голова просто болит..."
    show bg guesthouse2 with dissolve
    show Red at center
    show Host at left
    host "Спасибо вам большое! И простите, что мы скрывали от вас правду. Мы правда не хотели, но разбойники заставляли нас лгать путникам..."
    red "Мы вам верим. Но сейчас главарь мёртв, так что надеюсь на вашу честность и помощь"
    host "Всё что угодно! Я и все здесь присутствующие с радостью выполнят любое ваше поручение!"
    red "Для начала, скажите, сколько ещё разбойников осталось поблизости. Главарь же не в одиночку орудовал"
    host "Точно не скажу. Они поселились в старой усадьбе старейшины на горе, думаю человек десять"
    host "Понимаю, это небольшая банда. Но так как близ деревни никогда не было врагов, у нас попросту не было должного оружия, чтобы убить их, когда они вторглись в деревню"
    host "Три года назад они пришли ночью и перебили всех сторожей и собак. После направились к дому старейшины..."
    host "Только к утру мы поняли, какая беда нас настигла. Они захватили власть и принесли в доказательство голову..."
    host "Главарь выдвинул выжившим предложение: мы работаем на них, выращиваем для них еду, и докладываем обо всех путешественниках, которые прибыли в деревню"
    host "Странников они убивали и забирали их сбережения. Пока мы выполняли их приказы, банда нас не трогала"
    red "Всё ясно. Что же, не мне вас судить. Однако, необходимо окончить этот произвол. Позови сюда всех мужчин, чтобы к вечеру все были в таверне. И затушите фонари"
    hide Host with moveinleft
    me "Ред... Что ты задумал?"
    red "Разбойники рано или поздно заметят, что главарь пропал. Думаю, к вечеру они захотят лично проверить, не случилось ли с ничего. Тут их будет ждать наша засада"
    me "Ммм... Неплохой план. Я же могу чем-то ещё помочь?"
    red "Ты же только что был критически ранен, и уже предлагаешь свою помощь. Откуда такое рвение?"
    me "Я хочу отомстить за всех тех, кто пал от рук этих негодяев. Им нет прощенья"
    red "Ты правда так считаешь? Ну ладно, в таком случае, отдохни несколько часов, я дам знать, когда они явятся"
    hide Red with moveinright
    "Ред отошёл к входной двери и начал пересчитывать оставшиеся денежные сбережения. У меня же наконец выдался часок другой поспать и спокойно поразмышлять"
    "По видимому, в этой деревне нет моих родных. Если и были, то скорее всего сейчас убиты разбойниками. Может даже, если бы я пришёл сюда раньше, я бы успел их спасти..."
    "Но это уже никому не известно. Остались только те, кто убивал. Отребье, которое ни капли не ценит человеческие жизни. Язык не повернётся назвать их людьми"
    "Этот мир жесток. Но даже за этот короткий срок я уже повидал хороших людей... Чего стоит один Ред, спасший меня и приютивший. Я безгранично ему обязан и даже не знаю, как отплатить"
    "Размышляя о таких вещах, я не заметил, как начало постепенно темнеть. В таверне всё ещё горели свечи, но на улице началась сгущаться тьма"
    red "[me], ты не спишь там?"
    me "Нет, я в полном здравии. Ты что-то видишь, Ред?"
    red "Кажется, они здесь. Как я и предполагал, бандиты начали собираться на деревенской площади, я уже их вижу факела"
    red "Я сказал жителям спрятаться в домах и сидеть в засаде. в случае чего, я отдам команду для атаки"
    "Вдруг в дверь кто-то стукнул несколько раз. Затем произошла секундная пауза, и она была выбита. В комнату ворвались троё разбойников"
    image rogue2-1 = "images/rogue2.png"
    image rogue2-2 = "images/rogue2.png"
    image rogue2-3 = "images/rogue2.png"
    show rogue2-1 at left
    show rogue2-2 at center
    show rogue2-3 at right

    "Ред спрятался под столом и старался не показывывать виду. Я же встал в тени неподалёку от них и обнажил свой меч"
    "Разбойник: " "Кто здесь, а ну выходи! Я знаю, здесь точно кто-то есть!"
    me "Ты прав!"
    "Я выпрыгиваю из-за угла и вонзаю меч одному из бандитов в спину. Тот вскрикивает и бездыханно падает на деревянный пол, истекая кровью"
    "Вы наносите 100 ед. урона!"
    hide rogue2-2 with dissolve
    "Разбойник: " "Что за?! Это ты, сволочь, убил нашего главаря! Ты, ты поплатишься за это своей головой!"
    "С каменным лицом вытащив оружие из мёртвого тела, я посмотрел на двух оставшихся бандитов. В их глазах я видел злость перемешанную со страхом"
    me "Да, это сделал я. Ну что же, раз так хотите пасть от моего меча, то пожалуйста, нападайте"
    "Я твёрдо схватил меч в обе руки. Этих людей нет смысла бояться. По одной их боевой стойке видно, что у них совершенно нет боевого опыта"

    $ renpy.block_rollback()

    define rogue2 = None

    $ Player = player(level, xp, std_player_update)

    $ attacks = []
    $ attacks.append(attack("Разбойники набрасываются на вас с разных сторон!", std_base_attack, 25, 0))
    $ attacks.append(attack("Разбойники вместе наносят удары кинжалами!", std_base_attack, 20, 0))
    $ attacks.append(attack("Один из разбойников обходит вас сзади!", std_base_attack, 25, 0))

    $ rogue2 = enemy("Отряд разбойников", 250, std_enemy_update, std_enemy_rand)
    $ rogue2.attacks = attacks

    $ Log = log(std_win_check, std_lose_check, std_log_update, "Битва с разбойниками началась!")

    call screen fight_screen(Log, Player, rogue2)

    $ newLv = Player.add_xp(150)
    $ level = Player.level
    $ xp += 150

    $ renpy.block_rollback()
    hide rogue2-1 with dissolve
    hide rogue2-3 with dissolve
    "вы получаете 150 ед. опыта!"
    if newLv:
        "Ваш уровень повышен до [level]!"
    "Ещё двое разбойников упали на красный от крови пол. Их смерти были быстрыми и немучительными. Я же протёр свой меч и убрал его обратно в ножны"
    me "Царапины всё же оставили, гады. Но это ладно, заметных повреждений нет. Этот бой и в сравнение не шёл с битвой против главаря. Ред, ты там кстати как?"
    show Red at center with dissolve
    red "О-отлично... Быстро ты их, я аж удивился. Что это с тобой случилось, откуда такая непоколебимость?"
    me "Сам не знаю. Видимо, привык. Во всяком случае, троих уже нет, да и остальные должны были справиться. Мы победили?"
    "С улицы раздалось множество голосов, по ту сторону окон загорелись светящиеся огни факелов"
    "Мы с Редом поспешили на улицу, чтобы узнать, что же произошло. Там стояла толпа из крестьян, частично раненых, но радостных и улыбающихся"
    scene bg mountain_village with fade
    show Red at left
    show villager at center
    "К нам подбежал один из рабочих, в котором я узнал того самого, кто днём отказался со мной разговаривать и отправил в таверну"
    villager "Спасибо вам, Ред, спасибо вам, [me]! Без вас мы бы не справились! И извините за то, что неуважительно ответил вам тогда, я правда не хотел..."
    me "Ничего, я понимаю, что у вас и так была нелёгкая жизнь. Но трудное позади, ваша деревня теперь снова свободна"
    show Host at right with moveinright
    "Из толпы также вышел хозяин таверны, держащий в одной руке факел, а другой моток ткани с чем-то тяжёлым"
    host "Именно так! Нашей признательности нет границ. Быть может, мы бы и сами когда-нибудь одолели главаря, но точно не так скоро, без вас у жителей бы просто не хватило решимости"
    host "Я сожалею, что наше селение не может отплатить вам деньгами, так что примите от нас этот подарок..."
    "Мужчина развернул моток и достал оттуда сверкающий, отполированный, серебрянный меч"
    host "Пока вы отдыхали, наш кузнец отремонтировал меч главы разбойников. Я знаю, вам может быть совестно носить его, но это лучшее, что мы можем предложить..."
    "Меч главаря разбойников... Сколько же крови он пролил, используя это оружие? Достоин ли кто-либо носить его после такого?"
    define newSword = False
    menu:
        "Принять подарок":
            me "Спасибо вам большое. Я приму ваш подарок и буду использовать его во благо людей. Надеюсь хоть так удасться отмыть ту грязь и тот позор, оставленный его прежним владельцем"
            "Я взял у хозяина меч и вставил его в ножны взамен своего старого, подаренного Редом. Давно пора было его заменить, а то уж остриё совсем сточилось"
            host "Я рад, что вы не отказались. Теперь наш долг перед вами хоть чуточку стал меньше"
            $ newSword = True
        "Отклонить предложение":
            me "Извините... Я не могу принять ваше предложение. Лучше продайте его и заработайте немного денег для своей деревни, они нужны больше всего именно вам, а не мне"
            "Хозяин понимающе кивнул мне и завернул оружие обратно в ткань. Да, я конечно остался при своём старом мече, но он ещё немало времени мне сможет прослужить. Да и привык я к нему..."
            host "Хорошо, я постараюсь, чтобы он больше не пролил крови обычных людей. Раз такова ваша просьба, я её исполню"
    host "И да, я чуть было не забыл, что вы же путешественники. Хоть у нас и нет старейшины, но от имени деревни мы подготовили для вас грамоту с печатью"
    "Хозяин таверны достал из под куртки свёрток с красной печатью и протянул его мне. С виду это оказался обычный лист бумаги с лентой для фиксации"
    me "Спасибо большое вам всем за более-менее радушный приём. Мы бы хотели остаться у вас подольше, но нас всё ещё ждут дела. Я обязательно запомню вашу деревню и, быть может, когда-нибудь зайду сюда ещё разок"
    host "Будем вас с нетерпением ждать. Гарантирую, вы увидите, как сильно поменяется деревня в лучшую сторону к вашему возвращению!"
    hide Host with dissolve
    hide villager with dissolve
    hide Red with dissolve
    scene bg field with fade
    "Мы с Редом собрали все свои оставшиеся вещи, закинули рюкзаки за спины и снова отправились в путь. Это вряд ли была моя родная деревня, но я, как ни странно, не унывал, ведь шанс всё ещё оставался"
    "Моя цель не исчезла, нет, желание достичь её лишь стало сильнее. За время, проведённое здесь, я стал хоть немного опытнее, и это не могло меня не радовать. Я начал хоть немного понимать этот новый для меня мир"
    "Мы решили вернуться той же дорогой что и пришли, к счастью, тропа шла вниз и на юг, так что путь казался уже намного легче"
    me "Ну что, Ред? Давай устроим небольшой привал по пути, а утром отправимся дальше по нашему пути, что скажешь?"
    red "Привал? Ну-у, у меня конечно есть что-то вроде ткани для полатки, но я так обычно никогда не делал, лучше бы таверну какую найти..."
    me "Ты где тут таверну видишь? Давай уже, доставай вещи, я пока костёр разожгу, чтобы ночью теплее было"
    red "Ладно, чтоб тебя, не буду спорить, тем более когда сам устал. Сейчас сделаем тебе полатку"
    scene bg campfire with dissolve
    show Red at right
    "Я наломал несколько веток у деревьев и камнями разжёг пламя. Дерево задымилось, а затем разгорелось ярким теплым светом"
    "Ред же кое-как прибил колья и закинул сверху кусок ткани. Получился самодельный небольшой навес как раз под двоих человек"
    red "У меня ещё осталось пара бутербродов. Если ты не брезгливый, то можем на костре пожарить и съесть на ночь. Не пропадать же добру"
    me "И то верно. Я сейчас что угодно поглотить готов!"
    "Пока Ред жарил куски хлеба на палке над огнём, я решил немного потренироваться с мечом"
    if newSword:
        "Новый меч оказался весьма хорош. Движения с ним казались невероятно лёгкими, я будто чувствовал себя единым со своим оружием"
    else:
        "Даже старый меч теперь неплохо лежал в моих руках. Опыт в бою сделал мои движения намного легче и я чувствовал прилив сил в своих руках"
    red "Слушай, [me], а хочешь, я тебя одному приёму научу? А то я вижу твоё рвение к тренировкам, и так и хочется помочь"
    me "Приём? Конечно, я думаю овладеть новой техникой мне не помешает. Я и сам замечаю, что порой мои атаки слишком предсказуемы и однообразны"
    red "Вот и отлично! Только может ты не сразу сумеешь им грамотно воспользоваться в бою. Тут нужен опыт, а его у тебя ещё пока немного"
    me "Меньше слов, больше дела! Рассказывай, как им овладеть и в чём собственно он заключается"
    "Я присел на землю, положил рядом меч и начал внимательно слушать Реда"
    red "Я заметил, что ты очень часто атакуешь из засады, когда противник не подозревает о твоём присутствии. Это очень похвально, и этим надо пользоваться"
    red "Пока противник тебя не видит, есть возможность нанести один сильный удар. Само собой этот приём хорош только в самом начале боя, но и он может перевернуть исход сражения"
    me "Я заинтригован. Как же он называется?"
    red "Молниеносный удар. Путешествуя с отрядами стражи, я часто видел, как они его исполняли, и поэтому могу тебя ему научить. Для начала ты должен встать в боевую стойку и  занести меч сбоку от своего тела"
    "Я последовал совету Реда, встав, как он мне сказал. Это оказалось не очень удобно, так как меч тянул меня вбок, к тому же, подготовка заняла на порядок много времени"
    red "Да, примерно так. Давай, всё получается! Теперь, сделай резкий удар по площади, стараясь как можно быстрее провести лезвием по горизонтали. Я пока лучше отойду в сторону..."
    hide Red with moveinright
    me "Воооот так?!"
    scene bg campfire with fade
    "Я делаю длинный замах, но оступившись, роняю меч и падаю на холодную землю. Оказавшись весь в грязи, я не мог не расстроиться"
    me "Ну как так... Я же сделал всё верно, но всё равно ничего не получилось! Разве всё так плохо?"
    show Red at right with moveinright
    red "Ничего, я же сказал, что это будет нелегко. Возможно, я даже немного поспешил, ты тем более устал после сегодняшнего путешествия"
    me "Всё равно, я должен научиться! Иначе мне никогда не одолеть трудных врагов. Я понимаю, что пока что мои противники были далеко не самыми сильными"
    red "Я знаю, ты хочешь достигнуть совершенства, но это невозможно... Попробуй потренироваться самостоятельно, но лучше всё же подожди с использованием атаки на реальных врагах..."
    me "Может быть... Но я не сдамся! Как только моих тренировок будет достаточно, я покажу его тебе, и тогда ты не сможешь поверить своим глазам!"
    "Изучен новый приём: \"Молниеносный удар\"!"
    $ lightning_strike_claimed = True
    red "Ха-ха! Ну попробуй, я с радостью на это посмотрю и оценю. Я думаю будет весьма зрелищно"
    me "А то!\nТак, подожди... Ужин! Я проголодался а там твои бутерброды начинают подгорать!"
    red "Ой! И правда, нужно скорее снять их с огня!"
    show Red at center with moveinright
    "Ред бегом помчался к костру и вытащил поджаренные ломтики хлеба. Я же присел рядом на бревно и, положив рядом свой меч, отхлебнул из фляги воды"
    red "Вот, смотри какие красивые. Я успел их спасти от ужасной гибели в костре, и теперь они готовы к съедению!"
    "Ред с хрустом откусил один из кусков хлеба, а другой протянул мне. Недолго думая, я тоже вцепился в свой заслуженный \"кусок хлеба\""
    scene bg black with fade
    "Ночь в лесу оказалась глотком свежего воздуха для меня, и дала возможность наконец-то отоспаться. Я, словно ребёнок, окунулся в глубокий сладкий сон и проспал так до самого утра не размыкая глаз"
    scene bg field with fade
    "Как только наступило утро, я и Ред отправились обратно к развилке. На завтра есть особо было нечего, но это уже казалось обычным делом. Мы были готовы идти дальше, ведь впереди нас ждала деревня..."

    jump three_villages_road

label kria_village:
    $ expl_choice1 = False
    $ expl_choice2 = False

    $ stage = "Деревня Криа"
    $ chapter = 2
    $ save_name = "Глава " + str(chapter) + ". " + stage

    me "Что же, осталась последняя деревня. Деревня Криа. Ред, сколько примерно идти пешком?"
    "Ред достал карту и отмерил пальцами на ней несколько сантиметров, потом начал что-то бормотать под нос, видимо, считая"
    red "Километров десять - пятнадцать. Масштаб маленький, трудно точно сказать. Знаю, идти долго, но повозки или лошадей у нас нет"
    me "Да я привык уже. Кстати, а как мы до Луфтена-то доберёмся?! Ты же сам сказал, что мы недалеко от границы с Фандером, а столица на другом конце страны!"
    red "Эту проблему я уже обдумывал... В худшем случае - будем идти неделю - две, в лучшем - найдём повозку и доберёмся за пару дней"
    me "Ну ты и даешь... Если бы знал, попросил давно у местных повозку, они бы с радостью её дали. Блин, ну пошли так, что делать"
    red "Да извини, просто совестно такие вещи просить. Мы же всё-таки должны казаться состоятельными путешественниками!"
    me "По тебе видно..."
    hide Red with dissolve
    "С недовольным выражением лица я пошёл прямо по дороге в сторону далекой деревни. Это было последнее место, где я мог раньше жить, но мне уже слабо верилось, что я мог так далеко уйти"
    "Мы прошли с Редом немалый путь, и всё пока было зря. Конечно, мы нашли новых друзей, заработали хоть немного денег, но так и не смогли достичь первоначальной цели"
    "А в чём же тогда смысл? Сколько сил я вложил в осуществление моей мечты? Неужели всё это было зря, и не стоило даже пытаться?"
    "Я пока не мог ответить на эти вопросы. Мы шли всё дальше по полю, переходя небольшие ручьи и взбираясь на поросшие холмы"
    "По сравнению с лесной чащей и горными тропами, это место прельщало мне больше всего. Почему мы сразу сюда не пошли?"
    me "Слушай, Ред, я как-то забыл тебя спросить, а зачем нам эти грамоты с печатями? Жители упоминали, что их дают старейшины за выполненные задания, но их же даже продать не выйдет"
    red "А, грамоты! Да, их действительно дают по завершению квестов от имени деревни или доверенного писаря, и они должны храниться у путешественников до прибытия в столицу"
    scene bg guild_hall1 with dissolve
    red "В столице каждого из трёх городов есть гильдия. Большинство начинающих путешественников приходят туда, чтобы набрать заданий, а также получить некоторое спонсирование"
    red "Как понимаешь, достаточно трудно искать задания по всему материку, просматривая каждую деревню, особенно если деньги нужны как можно скорее"
    red "Поэтому все три страны по взаимному согласию решили создать места, в которые любой желающий может придти и оставить заявку о том, что ему нужна помощь от путешественников"
    red "Заявки размещаются на стендах в залах в нескольких экземплярах, так что любой может взять себе копию. Дальше всё решает скорость и правило: \"Кто первый, того и награда\""
    red "По негласному кодексту не принято пытаться выполнить одно и то же задание, не согласовав со всеми участниками, а также мешать другим"
    red "Этим правилам на удивление почти все следуют, но многие просто собирают листки и забывают о том, что кому-то действительно нужна помощь"
    red "Но, само собой, всё это не бесплатно. Гильдия существует не только благодаря городскому бюджету, но и на регулярных отчислениях деревень"
    red "Часть денег отправляется особенно успешным путешественникам ежемесячно, что ещё больше подогревает интерес к этой профессии. Монстров пока на всех хватает, хе-хе"
    red "Выполнив задание, путешественник помимо награды за свои труды получает грамоту. Её он и должен принести в гильдию в качестве подтверждения. Для начала, необходимо всего одна - она позволит тебе стать официальным членом гильдии"
    red "Также за определённое число выполненных заданий можно получить повышение, которое увеличивает ежемесячный доход. Это называется рангом гильдии"
    red "Единственная проблема - особо высокие ранги просто так получить не получиться, нужно официальное подтверждение короля. К тому же, ранг у одной гильдии не действителен в других, но это вроде хотели исправить"
    scene bg field with fade
    show Red at center
    me "Ого, так подумать, быть членом гильдии действительно очень прибыльно - выполняешь задания, помогаешь нуждающимся, а тебе ешё и платят за это!"
    red "Да, всё именно так, поэтому путешественников и становится всё больше. Правда, многие на первых заданиях и погибают, переоценив свои силы, напав на слишком опасного монстра"
    me "Хм, ну, я надеюсь мне это не грозит. Но я думаю, вступить всё же стоит, соблазн получить лишние деньги достаточно велик. Да и проще будет..."
    red "Ты мыслишь прямо как я, только... Разве ты не хотел найти там своих родных и зажить спокойной жизнью в своём родном селении?"
    me "Да... Только боюсь спокойно жить уже не получится. Я в любом случае отправлюсь в столицу вместе с тобой, Ред"
    red "Хо, приятно это слышать. Составишь мне компанию. Но! Не унывать раньше времени, ещё не всё потеряно!"
    me "Согласен! Сколько ещё идти до деревни Криа, если не секрет?"
    "Ред осмотрелся вокруг и остановил свой взгляд на странной скале в форме зуба"
    red "О, да мы кстати уже почти пришли! Видишь этот острый камень? Прямо за ним находится холм, а за ним нас и ждёт долгожданная деревня!"
    red "По легенде - это зуб дракона. Они раньше действительно жили на материке, но уже прошло уже много лет, с тех пор как их кто-то видел"
    red "Скорее всего это просто байка, чтобы заинтересовать путешественников... Эй, ты куда это понёсся?!"
    hide Red with dissolve
    "Узнав, что Криа находится совсем рядом, я чуть ли не вприпрыжку понёсся в сторону холма. Он, к слову оказался совсем не за скалой, а в километре по полю, но это само собой меня не остановило"
    red "Да подожди! Я же не успеваю за тобой, сколько можно повторять, что я уже не молод, да и вообще, устал, есть хочу и спать..."
    me "Как ты можешь такое говорить, когда мы уже почти у цели? Вот, я уже вижу крышу дома вдали!"
    scene bg destroyed_village1 with fade
    "Волна шока пронзила меня, когда я вбежал на холм. Ноги будто вросли землю, время вокруг остановилось, пока я стоял с прикованным к развалинам взглядом"
    me "Как так... Деревня... Этого же не может быть, да, Ред? Мы снова опоздали..."
    "Рядом со мной встал Ред. Я краем глаза увидел, что он тоже выглядит шокированным. В его глазах я даже заметил какую-то безымянную жалость"
    me "Кто... Кто это мог сделать? Целая деревня уничтожена, здесь ни осталось ни души, даже птиц не слышно"
    red "Я не знаю. Я и сам не могу поверить, что такое могло случиться. На такое разбойники не способны..."
    me "Как же так? Получается, что всё было напрасно? Ведь последняя надежда было именно это место"
    red "Боюсь, что так. Нужно осмотреть это место, не исключено, что здесь остались следы выживших или просто какие-то сведения о случившемся"
    me "Да, ты прав. Клянусь, если я найду того, кто это сделал, живым его свет уже не увидит"
    "Я обнажил свой меч и спустился с холма на деревенскую площадь. Ред медленно двинулся за мной, рассматривая по пути разрушенные ограждения и сломанные столбы, некогда служившие как фонари дл освещения"
    me "Очень странное место. Такое ощущение, что на меня давит какая-то неестественная сила. Ред, ты ничего не ощущаешь?"
    red "Ты прав, я тоже что-то чувствую, но пока не могу понять, что это может быть. Не хочу заранее вводить тебя в заблуждение своими догадками"
    me "От твоих слов мне стало ещё хуже. Ладно, давай осмотрим ближайшие здания, нечего попусту время терять"
label Kria_choices:
    if expl_choice1 and expl_choice2 and expl_choice3:
        $ expl_choice1 = False
        $ expl_choice2 = False
        $ expl_choice3 = False
        jump road_to_luften
    menu:
        "Осмотреть разрушенную лачугу" if not expl_choice1:
            $ expl_choice1 = True
            "Я пошёл в сторону почти развалившейся лачуги, стоявшей на окраине деревни. Аккуратно перешагнув через провалившийся порог, я оказался внутри единственной комнаты"
            me "Ред, жди здесь. Если что увидишь - тут же дай знать. Я пока осмотрю тот обрушившийся дом"
            scene bg destroyed_house1 with dissolve
            "Место оказалось полностью уничтоженным, будто ураган прошёлся насквозь этого крошечного жилища. Кругом валялись обломки, все стёкла были разбиты, потолок провален"
            "Шагая ботинками по осколкам, я медленно прошёл по комнате. Трупов нигде не было, как и следовь крови. Только сломанные предметы интерьера. Было похоже, что жители бежали в спешке из зданий"
            "Подойдя к сломанному столу, я осмотрел бывшее запылённое рабочее место. Раньше тут лежали какие-то бумаги, но теперь все они обратились в пепел или рассыпались на кусочки"
            me "А это что такое? Кажется, этот листок почти новый, чернильная клякса ещё не высохла"
            "Я аккуратно достал из под упавшей доски порванный лист вместе с конвертом. Это оказалось письмо одного из жителей: "
            me "Капитану Тунру от старого знакомого... Приходите к моему племяннику в столице... Надеюсь, вы рассмотрите дело в кратчайшие сроки..."
            me "Мда, бред какой-то. Почти все записи замазаны или размыты. Но это интересно, нужно будет разузнать у Реда, кто этот капитан Тунр"
            "Я также аккуратно покинул лагучу и вернулся на поляну. Ред по-прежнему ходил там, тоже о чём-то размышляя, так что я пока не стал расспрашивать об найденных мной вещах"
            scene bg destroyed_village1 with dissolve
            jump Kria_choices
        "Осмотреть старую церковь" if not expl_choice2:
            $ expl_choice2 = True
            me "Давай осмотрим ту старую церковь, мне кажется, это наиболее сохранившееся место после этой катастрофы"
            red "Как скажешь, только давай осторожней, было бы не очень весело, если что-то обрушиться, пока мы внутри"
            me "Надеюсь это шутка такая. Чем быстрее мы всё осмотрим, тем выше шанс, что что-либо узнаем"
            scene bg destroyed_church with fade
            "Мы прошли внутрь здания через распахнутую дверь. Это оказалось довольно старая церковь, за которой, думаю, никогда толком не следили"
            me "Тут темно... Окна все запылились, свет не проходит. Много поломанных скамеек, целая груда досок лежит в углу. Ред, ты что-то чувствуешь?"
            red "Тут тоже есть какое-то давление, но сила ниже, чем снаружи. Я думаю, церковь сохранилась именно поэтому, она была далеко от источника"
            "Мы осмотрели здание беглым взглядом и решили покинуть данное место. Я не нашёл ничего интересного помимо каких-то бумаг с церковными песнями, и решил не задерживаться а помещении"
            scene bg destroyed_village1 with dissolve
            jump Kria_choices
        "Осмотреть деревенскую площадь" if not expl_choice3:
            me "Предлагаю осмотреть деревенскую площадь. У меня чувство, что там что-то есть"
            "Ред медленно пошёл в центральную часть деревни вместе со мной. Это оказалась небольшая протоптанная поляна со столбом посередине"
            me "Похоже раньше на столбе висел флаг. Судя по ошмёткам на земле, его вполне могло сдуть ветром. Ред, ты как считаешь, это был ураган?"
            show Red at center with dissolve
            red "Нет, мне кажется это нечто другое, более страшное..."
            me "Что ты имеешь в виду?"
            red "Разве ты не чувствуешь, как сильно здесь давит на тебя воздух? Эта сила намного сильнее, чем где-либо ещё  в деревне"
            me "Я подумал, что это из-за прошедшей грозы... Но ты же считаешь иначе? Не молчи! Что всё это значит?"
            red "Такое давление ощущается после высвобождения колоссального количества магической энергии. Оно должно проходить в течение нескольких часов, но похоже, что катастрофа случилась уже давно"
            me "Хочешь сказать... Что использованная магия была очень сильна? Такое же возможно?"
            red "Наверное. Но я понятия не имею, кто мог обладать такой силой и зачем он воспользовался ей в этой деревне. По одним магическим следам трудно сказать"
            $ expl_choice3 = True
            jump Kria_choices
label road_to_luften:
    "Вдруг на соседней деревенской уличе раздался ужасный грохот и шум приближайщихся колёс. Я так резко вздрогнул, что чуть было не сбил Реда"
    me "Это люди? Они ещё здесь?"
    "Прогремел второй удар, по видимому какой-то массивный объект врезался в здание. Я обнажил меч и побежал в сторону, откуда доносился звук"
    hide Red with dissolve
    "Пробежав по дороге, я увидел повозку, протаранившую лагучу. Лошади уже нигде не было, а кучер лежал на земле, держась одной рукой за кровоточащий лоб"
    scene bg destroyed_house1 with fade
    "Я быстро забежал в здание. повозка застряла между сваями, подпирая крышу своим собственным весом. Потолок постепенно осыпался"
    me "Эй, что с вами? Вы ещё живы? Что здесь чёрт возьми произошло?"
    "Я подбежал к мужчине и помог ему подняться. Это оказался обычный житель средних лет в небогатой одежде. Рана была не серьёзная, он был всё ещё в сознании"
    show traveller at center with dissolve
    "Мужчина: " "С-спасибо вам... Я... Кто вы такой?"
    me "[me]. Но сейчас это не так важно. Скажите, откуда вы и что с вами случилось?"
    djoun "Я... Джоун, извозчик, доставляю товары и посылки по деревням... Постойте, где я сейчас нахожусь? Что с моей лошадью?!"
    me "Вы в деревне Криа. Я понятия не имею, что с вами произошло, но, как видите, ваша повозка оказалась в здании, а конь сбежал"
    me "Давайте быстрее покинем это место, умоляю вас. Здесь всё может обрушиться с минуты на минуту!"
    "Не дожидаясь ответа от до сих пор находящегося в шоке Джоуна, я вытащил мужика наружу. К тому моменту Ред уже стоял там, осматривая следы от свернувшей не туда повозки"
    scene bg destroyed_village1 with fade
    show traveller at center
    show Red at left
    red "Мда, господин Джоун, как же вас так угораздило в дом врезаться... За дорогой следить надо"
    me "Ред, давай без шуток. Лучше помоги раненному"
    me "Джоун, что с вами случилось? Расскажите, пожалуйста, нам очень важно знать, особенно если это связано с этой деревней"
    "Пока Ред наматывал повязку на голову, мужчина начал рассказ о том, как он оказался в деревне Криа"
    djoun "Я живу в одной из деревень недалёко от столицы. Работаю извозчиком, ещё часто доставляю посылки по стране"
    djoun "Пару дней назад я получил письмо из деревни Криа с просьбой забрать посылку и доставить её в столицу. Вот и приехал сюда"
    me "Насколько быстро по Луфтену доходят письма? Пожалуйста, скажите хоть примерно, сколько времени прошло!"
    djoun "Не знаю, дней пять, иногда быстрее. Получается, неделя прошла, как отсюда письмо выслали. А что такого-то?"
    me "Мне важно знать, сколько дней прошло с тех пор, как люди исчезли. Я ищу... я ищу кое-кого"
    red "Ладно, это понятно. Скажи лучше, как ты в дом врезаться умудрился? Вроде не пьяный, дорога не скользкая"
    djoun "Как в дом врезался? Да я и не помню... Только если не..."
    "Лицо Джоуна помрачнело, а глаза стали большими и круглыми. Вспоминая, что-то, он завис, упёршись взглядом в одну точку"
    red "Что?! Что случилось, говори!"
    djoun "К-кабан..."
    me "Кабан? На тебя напал кабан и ты из-за этого врезался в здание?"
    djoun "Вы не понимаете... О-обернитесь, п-прошу вас!!!"
    "Я вздрогнул, краем глаза заметив на горизонте приближающееся тело. В этот же момент по земле прошёл толчок"
    hide Red
    hide traveller
    image boar = "images/boar.png"
    show boar with fade
    "Это было огромное существо, только отдалённо напоминающее тех кабанов, которых я знал. С каждым шагом его, я ощущал ту силу, которая от него исходит"
    me "Ред, что это такое?.. Это он является причиной катастрофы в деревне?"
    "Старик выглядел испуганным не меньше меня. По его лицу я понял, что раньше он никогда не видел такого существа"
    red "Возможно... Но я не хочу сейчас это выяснять, нужно скорее бежать, иначе нам не здоровать"
    "Монстр посмотрел в нашу сторону и медленными шагам начал приближаться. Используя свои бивни, кабан сломал разделявший нас забор, будто его и не было"
    hide boar with fade
    show Red at center
    me "Ред. Я боюсь придётся драться. Не думаю, что мы так просто отделаемся"
    red "[me], ты спятил?! Ты не сможешь одолеть его, его сила не сравниться ни с каким троллем!"
    me "Всё равно. Я должен. У нас нет ни лошадей, ни повозки. Так что единственный способ - убить эту тварь"
    red "Чёрт, ну раз так, то тебе точно не справиться своими силами. Это будет глупая смерть, не находишь?"
    me "Ты можешь как-то мне помочь?"
    red "Возможно... Да, у меня есть одна идея. Я хранил одно зелье на чёрный день, оно очень дорого стоит, но видимо это подходящий случай, подойди ближе, [me]"
    "Ред встал рядом со мной и протянул вытащенный из кармана пузырёк с фиолетовой жидкостью. Он был с какими-то иноязычными пометками и герметично упакован, выглядел довольно старым"
    me "Что это? Какое-то особое зелье?"
    red "Типо того. Ты должен выпить его, и тогда получишь прирост к своим способностям. Сделай всё быстро, пока эффект не иссяк, с ним у тебя есть хоть какой-то шанс победить"
    me "Я тебя понял. Отведи пока Джоуна на безопасное расстояние, и поищи его лошадь. Я же приму бой прямо здесь"
    "Как обычно достав свой меч, я приготовился к сражению, пузырёк лежал у меня в левой руке, я был готов в любой момент опустошить его"
    hide Red
    show boar with fade
    "Кабан прошёл на деревенскую площадь и остановился в двадцати метрах от меня. Мы обменялись взглядами, если так можно назвать те четыре светящихся пятна"
    "Когда этот зверь подошёл ближе, я увидел, что он полностью отличен от обычной лесной твари"
    "Тело его было покрыто каменной чешуей, спина поросла травой, а бивни его были словно гранит. Размер его был с целую небольшую лачугу"
    "Только когда он оказался настолько близко, я почувствовал, что от него исходит та самая энергия, которая давила на меня и Реда в деревне"
    "Если этот монстр и есть причина гибели целой деревни - то у меня просто нет другого выбора, кроме как уничтожить его прямо здесь, на месте его злодеяний!"
    "Не затягивая времени, я вырвал заглушку из колбы и залпом выпил алхимическую смесь. После протяжного глотка по телу моему будто пробежал энергетический заряд"
    scene bg black with fade
    "Внезапно я почувствовал необычайную лёгкость. Меч в руках лежал словно перо, я совершенно не чувствовал десяток килограмм в своих руках"
    "Здоровье увеличено на 100\%"
    "Сопротивление физическому урону увеличено на 80\%"
    "Сопротивление магическому урону увеличено на 50\%"
    "Сопротивление яду увеличено на 100\%"
    "Сопротивление огню увеличено на 70\%"
    "Скорость атак увеличена на 200\%"
    me "Я ощущаю... Невероятную силу... Что это за зелье такое?"
    scene bg destroyed_village1 with fade
    show boar
    "Все мои физические показатели мгновенно улучшились в несколько раз. Не знаю, как такое вообще возможно, но теперь я уверен, что смогу победить в схватке"
    "Кабан, заметив, что я всё ещё стою на месте, кинулся на меня. Недолго думая, я отскочил на пару метров вправо, оставив зверя в недоумении"
    me "Ну давай, покажи на что способен!"
    $ renpy.block_rollback()

    define boar = None

    $ Player = player(level, xp, std_player_update)
    $ Player.max_health += Player.max_health
    $ Player.health = Player.max_health
    $ Player.attacks.append(attack("Молниеносный удар", lightning_attack, value = Player.max_damage, cost = 2))

    $ attacks = []
    $ attacks.append(attack("Кабан сотрясает землю своими движениями!", std_base_attack, 25, 0))
    $ attacks.append(attack("Кабан несётся на вас, выставив бивни вперёд!", std_base_attack, 20, 0))
    $ attacks.append(attack("Кабан делает резкий прыжок в вашу сторону!", std_base_attack, 30, 0))
    $ attacks.append(attack("Глаза кабана внезапно вспыхивают красным пламенем!", std_block_attack, 5, 0))
    $ attacks.append(attack("Кабан издаёт ужасающий рокот,\n оглушающий вас в одно мгновение!", std_base_attack, 100, 0))

    $ boar = enemy("Кабан Каменной Скалы", 1000, std_enemy_update, std_enemy_rand)
    $ boar.attacks = attacks

    $ Log = log(std_win_check, std_lose_check, std_log_update, "Началась битва с Кабаном Каменной скалы!")

    call screen fight_screen(Log, Player, boar)

    $ newLv = Player.add_xp(500)
    $ level = Player.level
    $ xp += 500

    $ renpy.block_rollback()

    "Я оббегаю кабана со спины и вонзаю в его бок свой острый меч. Не выдержав очередного удара, каменная чешуя рассыпается, высвобождая бурлящий фонтан крови"
    "Кабан издаёт последний протяжный рык, после чего бездыханно падает на землю в расстёкшуюся под ним лужу своей же бардово-чёрной крови"
    hide boar with dissolve
    "Действие эффекта зелья иссякает\nИзначальные характеристики восстановлены"
    "вы получаете 500 ед. опыта!"
    if newLv:
        "Ваш уровень повышен до [level]!"
    "Бой завершён. Я победил этого монстра, ни смотря на его колоссальную силу, и теперь его туша будто склонившись лежит перед моими ногами"
    show Red at center with moveinright
    red "удивительное создание... Ума не приложу, как такой монстр мог оказаться в стой мирной деревушке"
    "Я, нервно дыша, присел на траву и положил меч рядом. По моему лбу струился холодный пот"
    me "Это же не обычный кабан, откуда он мог взяться? И почему во время битвы с ним я почувствовал магическую энергию, как тогда на площади?"
    red "Гхм, магия? Тогда у меня наверное есть идея. Понимаешь ли, от существ может исходить магические потоки либо когда они сами обладают магией, либо когда их призвали заклинанием"
    me "Заклинанием?! Хочешь сказать, что этот огромный монстр был кем-то создан?"
    red "Скорее всего так. Но у меня самого в голове не укладывается, сколько на это было за затрачено маны... Ну, магической энергии"
    red "Такие вещи под силу разве что бриллиантовым членами гильдии или самому королю, но никак не обычному человеку"
    me "Бриллиантовые члены гильдий? Так называются люди, получившие высший ранг?"
    red "Именно, это самые известные и могущественные рыцари Инзеля. Но ни один из них бы не стал использовать свою силу во вред"
    red "Если есть ещё кто-то, то нужно обязательно сообщить об этом в столице. Я возьму чешую кабана и покажу её там в качестве доказательства"
    "Ред наклонился к останкам и оторвал окаменевший кусок кожи монстра. Удостоверившись, что он совершенно безопасен, старик положил его к себе в рюкзак"
    me "Эх, так и знал, что мы ничего не найдём. Всё же не суждено мне узнать своё прошлое..."
    "Пока я стоял посреди развалин некогда процветавшей деревни, волна грусти снова накрыла меня. Ни в одной из трёх деревень я ни нашёл ответов"
    me "Видимо, всё же придётся поехать с тобой, Ред. Некуда больше идти..."
    red "Да, не переживай ты так, я с радостью отправлюсь вместе с тобой в Луфтен. Только вот, на чём?"
    show traveller at left with moveinleft
    "Мы с Редом ухмылкой бросили взгляд на Джоуна, стоявшего всё это в стороне, ужасаясь окровавленному трупу кабана"
    djoun "А? Что... я?"
    red "Ну да. Мы тебе жизнь спасли? Спасли. Монстра убили? Убили. С тебя так-то причитается, вознаграждение там какое-нибудь"
    djoun "В-вознаграждение? Да это, нет у меня ничего, деньги все уже истратил, повозка сломана да и дом мой неблизко. Как же я могу отплатить?"
    red "Ты не беспокойся, я уже придумал, как ты расплатиться сможешь. Лошадь свою найти сможешь?"
    djoun "Смогу, только... Нет, лошадь отдать не могу, как же я без неё!"
    red "Тьфу, да нет, ты неправильно понял. У меня к тебе другое предложение есть"
    djoun "Это какое же предложение?"
    red "Ты находишь своего жеребца, запрягаешь в повозку и быстро довозишь нас до Луфтена. Всё, больше ничего не требую. Идёт?"
    djoun "Идёт. Всё равно в столицу вернуться хотел, так что доставлю вас с радостью! Только это, повозку помогите вытащить, а то я один не справлюсь"
    show destroyed_house1 with dissolve
    "Мы втроём вернулись к тому дому, куда врезалась повозка Джоуна. Аккуратно осмотрев место происшествия и убедясь, что всё, что могло обрушиться, уже обрушено, мы приступили к извлечению повозки из лачуги"
    red "К счастью, колёса и крепления целы, только корпус сверху поломан. Кароче, поедет, до города сто пудов довезёт"
    "Пока мы копались с ремонтром корпуса, Джоун смог таки отыскать свою лошадь на соседнем поле, мирно пасущуюся, словно ничего и не было"
    show destroyed_village1 with fade
    "К вечеру все наконец было взборе, конь запряжен, а повозка готова к отправке. Мы с Редом провозились пару часов, чтобы найти в деревне хотя бы обычный молоток, чтобы прибить гвозди, но это того стоило"
    show traveller at center with moveinbottom
    djoun "Спасибо вам огромное, даже не знаю, как бы я без вас вернулся отсюда! Повозку один бы точно не починил"
    show Red at right with moveinright
    red "Благодарности будут, когда до города доберёмя. Всё-таки, путь не близкий, да и не простой"
    djoun "Доберёмся! Зуб даю! Мой конь нас мигом довезёт, и дня не пройдет. А дорогу я как свои пять пальцев знаю"
    red "Ну что же, будем надеяться. [me], давай, залезай в повозку!"
    hide traveller with moveinbottom
    "Я запрыгнул внутрь и уселся на лавку лицом к Реду. Джоун залез спереди и взял поводья в руки. Всё было готово к отбытию"
    djoun "Но! Пошла!"

    scene bg mountains1 with dissolve

    "Лошадь заржала и тронулась в путь по старой полевой дороге. Пустая и бездушная деревня Криа начала скрываться за горизонтом, а наша повозка уходила всё дальше в безграничное поле"
    me "Хорошо здесь... Так тихо, ни души. Словно во сне едешь, ни о чём не думаешь. Только после ожесточённых схваток начинаешь ценить такие моменты"
    red "Да, тут не поспоришь, хорошее место. Мне конечно не впервой, но сегодня особенно красиво. Слушай, хочешь историю расскажу, пока едем?"
    me "А давай, я не против послушать. О чём она, о твоих странствиях?"
    red "Нет, к сожалению. Но тебе всё равно понравится. Это история о битве с пламенным драконом"
    me "Ого, драконы. Ты же сказал, что они давно вымерли, разве нет?"
    red "Ну я погорячился, последний из них умер всего навсего лет двадцать назад. О нём и пойдёт речь"
    djoun "О, а я знаю, это тот, который в вулкане жил..."
    red "Раз знаешь, так молчи и делом занимайся, я всё равно расскажу. Ну так вот..."
    "Я устроился в лежачей позе на скамье, закрыл глаза и начал слушать рассказ Реда. Повозка правда то и дело напиралась на камни, не давая заснуть, но сейчас это было даже и к лучшему"
    red "Двадцать лет назад началось событие, которое предрекали пророчества уже не одну сотню лет. Позднее оно было названо Великой Битвой Пламени"
    red "Всё началось с того, что экспедиция от королевства Мариэн направилась к северной части Великого Хребта, где располагался вулкан Адского Пламени, самая большая гора во всем Инзеле"
    red "Поводом к этому послужили известия о надвигающимся его извержении, происходящем раз в одну тысячу лет. Цикл в то время как раз и подходил к концу"

    scene bg flame_dragon with dissolve

    red "Легенды гласили, что в недрах этого вулкана спит легендарный дракон, которому нипочём ни ветра, ни огонь, ни камень"
    red "Раз в одну тысячу лет монстр этот пробуждается от спячки и выходит наружу, чтобы снять слой затвердевшей магмы, сковывашей его на протяжении сна"
    red "Выбираясь из огненного горнилы, дракон в буйстве уничтожал всё живое на континенте - растения, животных, людей. Единицам удавалось остаться в живых"
    red "Именно поэтому у людей ничего не сохранилось о событиях раньше этого периода - все государства и записи попросту обращались в пепел, разве что оставались подземные хранилища, которые сейчас заброшены или разграблены"
    red "К счастью, событие это происходило не внезапно. Так как дракон ломал слой магмы достаточно долго, о приближающейся катастрофе можно было догадаться где-то за месяц, всего лишь наблюдая за вулканом"
    red "Когда дракон пробуждается, вулкан начинает бурлить и медленно выпускать из себя лаву, уничтожающую всё живое в округе"
    red "Правители государств знали, что если не расправиться с драконом, то мир снова впадет  в хаос, а все нажитое таким трудом придется восстанавливать не один десяток лет"
    red "Однако, никто не хотел принимать каких-либо активным действий, ведь в истории ни кому ещё не удавалось одолевать таких ужасных монстров, как Пламенный Дракон"
    red "Только благодаря императору Мариэна, Вингерму, удалось собрать совет трёх королевств, в ходе совещаний которого и было предложено объединиться для борьбы против общей угрозы"
    red "Вингерм выступил с объяснением о том, что он лично возглавит отряд из элитных магов и бойцов Мариэна, которые одолеют Пламенного Дракона и наконец оборвут этот бесконечный цикл разрушений и смертей"
    red "Выслушав его, Фандер и Луфтен всё же решились принять участие в этой рискованной операции, и вскоре отряд из десяти тысяч бойцов был сформирован и направился к подножию извергающегося вулкана"
    red "В ночь на летнее солнцестояние закрытое дымом небо внезапно озарилось ярким красным пламенем. Это был оно, огромное создание размером с целый город, смотревшее но толпу людей сквозь облака"
    red "Воины трёх королевств застыли в расстеряности, не зная, что делать. Многие пытались бежать, но спотыкались, и падали в кипящую лаву, стекающую по склону горы"
    red "Люди не были готовы к схватке с таким чудищем, началась паника, нужно было скорее что-то предпринять, иначе битва бы кончилась даже не начавшись"

    show Wingerm at center with fade

    red "И тогда раздался он, возглас короля Мариэна, Вингерма: \"Впёред, воины! Нам некуда бежать! Сейчас решается судьба всего мира, всего человечества! И она в наших руках!\""
    red "Эти слова прокатились грохотом по всему склону, и на минуту всё будто затихло. А затем раздались воинственные людские крики, сравнимые с рёвом вулкана"
    red "Так начался кровопролитный бой. Тысячи людей ринулись в наставление, словно волна бушующего моря"

    hide Wingerm with dissolve

    red "На передовой оказались самые лучшие воины континента - Цвайн, легендарный мечник Инзеля, Штрауф, главнокомандующий армии Луфтена и сэр Готтвальд IV, наисильнейший маг огня в мире"
    red "Совместные усилия этих троих смогли сдержать дракона и не выпустить его за пределы хребта. Далее в бой уже вступили маги Мариэна"
    red "С помощью сильнейших заклинаний им удалось запечатать дракона в камне на некоторое время, не дав ему взмыть в небо и дав возможность атаковать пехоте"
    red "Отряды воинов Фандера и Луфтена начали подъем в гору. Сотни рук одновременно ударили по лапам Дракона, и они разлетелись на куски"
    red "Тварь издала ужасный вой, но все ещё была жива. Нужен был тот, кто смог бы нанести финальный удар по огромной голове"
    red "Пока все были в замешательстве, в небе внезапно вспыхнула голубая молния, и тело дракона было разрубленно надвое, словно огромным ножом"
    red "Это был Цвайн. Используя таинственный артефакт, он направил всю свою магическую энергию в один смертельный удар мечом"
    red "Бездыханное тело пало на склон, разлившись морем крови. Кровавая битва была наконец окончена"

    scene bg mountains1 with dissolve

    red "Это был великий день. Мировая угроза была уничтожена, и больше людям можно было не опасаться надвигающегося апокалипсиса"
    red "В битве пало несколько тысяч человек. Их жизни никогда не будут забыты Инзелем. Меня не было среди солдат, но многие мои знакомые тогда погибли"
    red "Самое главное, в этом сражении люди показали, что они все ещё могут сплотиться ради общего блага, не смотря на внутренние разногласия"
    red "Конечно, Фандер так и остался почти изолированной страной, а Мариэн по прежнему не желает делиться своими тайнами, но всё же мир стал чуть спокойнее, а люди добрее"
    me "Хорошая история. Она многое дала мне понять. Ред, будет время, расскажешь поподробнее о тех воинах, которых ты упоминал в повести? У меня остались кое-какие вопросы"
    red "Да хоть завтра, конечно расскажу! Инзель вообще богатый на всяких выделяющихся персон, и некоторых точно стоит знать"
    red "Но не сейчас. Я что-то заговорился, глубокая ночь наступила. Пора бы и на боковую"
    "Не дожидаясь моего ответа, Ред опрокинулся на скамейку и захрапел"
    me "Спать?.. Джоун, вы там сами не устали, может заменить вас?"
    "Я привстал в повозке и подошёл к нашему кучеру. Тот спокойно держал узды и вёл лошадь по полевой дороге"
    djoun "Отдыхайте, мне-то нормально, я привык. А у вас сегодня тяжёлый день был, отсыпайтесь. Обещаю, как подъезжать будем, разбужу!"
    me "Ладно, спасибо вам. Тогда я тоже вздремну хоть часиков пять"
    scene bg black with dissolve
    "Последовав примеру Реда, я тоже снял сумку, улёгся на лавку и, убаюкиваемый покачиванием повозки, погрузился в сладкий сон"
    "За последнее время я так уставал, что совершенно не видел снов. Не знаю, в чем причина, может и в моей памяти... Хотя, кого это сейчас волнует?"
    scene bg black with dissolve

    $ stage = "Луфтен"
    $ chapter = 3
    $ save_name = "Глава " + str(chapter) + ". " + stage
    define duel_won = False
    define new_skill_claimed = False

    "Ночь прошла для меня незаметно. Я был готов поспать ещё часик-другой, если бы Ред не начал меня яростно тормошить"
    me "Что опять случилось... Где пожар, кого бить?"
    red "Давай, вставай, мы почти приехали! Луфтен в километрах пяти"
    "Ещё сонный, я попытался встать и осмотреться. Сквозь слипшиеся от сна глаза я увидел невообразимую картину, от которой мурашки пробежали по всему телу"
    scene bg luften1 with dissolve
    "На краю повозки стоял Ред, одной ногой оперевшись на его борт. Он любовался этим видом, впитывая в себя ту яркую красоту, которую излучал город"
    red "Вот он - самый большой город континента. Мы наконец добрались до него!"
    "Сотни, нет, тысячи домов раскинулись на склоне огромного холма, выходящего на лазурное чистое море"
    "Десятки кораблей качались на воде, пришвартованные к многокилометровой пристани. И всё это было наполнено неисчислимыми толпами людей"
    me "Вот он какой, Луфтен... Не увидев собственнолично, никогда бы не смог поверить рассказам о его красоте!"
    "Колёса повозки быстро стучали о мощённую каменным кирпичом дорогу. Мимо нас проносились то и дело другие экипажи, кони, пробегали путешественники и рыцари"
    "Ещё чуть-чуть, и наш состав въехал в огромные замковые ворота, отделявшие городской сектор столицы от остальных деревень. Мы официально вступили на порог Луфтена"
    scene bg luften2 with dissolve
    "Повозка проехала в жилой квартал. Народу здесь было не так много, и можно было наконец остановится"
    "Привязав лошадь к изгороди одного из домов, Джоун слез с повозки и помог нам с Редом спустить все свои вещи"
    show traveller at center with dissolve
    show Red at right with dissolve
    djoun "Вот и всё. Вы теперь в Луфтене, я как видите своё дело выполнил. Дальше уж сами, мне ехать по делам надо"
    me "Было приятно познакомиться, Джоун. Надеюсь мы ещё как-нибудь увидимся"
    djoun "Всё может быть, всё может. Пока, друзья!"
    "Джоун забрался обратно в экапиж, и поехал по мостовой дальше по улице. Ещё мгновенье, и он скрылся за поворотом, словно его никогда и не было"
    hide traveller with dissolve
    show Red at center with moveinright
    red "Хороший мужик, добрый... Ой, а это ещё что такое?"
    "Ред наклонился и подобрал с земли шкатулку, закрытую на замок, с прикрепленным к ней биркой"
    "Я заинтересованно подошёл поближе и осмотрел найденный Редом предмет"
    red "Алхимическая лавка Луфтена. Доставить не вскрывая. Похоже, это обронил Джоун, когда спускал наши вещи. И он уже уехал..."
    me "Ну так нужно найти эту лавку! Вдруг там что-то очень важное, и поэтому Джоун так спешил"
    red "Не думаю... Хотя, раз она теперь у нас, то и денег мы сможем с неё получить. Можно поискать, правда лавок этих здесь тысячи"
    "Я попросил у Реда шкатулку и положил её к себе в сумку. Пусть пока полежит у меня, а как найдётся лишний денёк, займусь ей"
    me "Так, это ещё успеем сделать. А сейчас - Луфтен! Куда нам идти, Ред? Это же твой родной город, как никак"
    red "Хм, хороший вопрос. Нужно поискать дом, в котором мы могли бы остановиться. Также нам нужны задания, их получают в городской гильдии"
    red "Не помешает заглянуть на местный рынок, там продаются оружия, еда, зелья. И наконец, надо отдать посылку владельцу"
    me "Сколько вариантов... Ладно, сейчас подумаю"
    define expl_choice4 = False

label luften_explore:
    if expl_choice1 and expl_choice2 and expl_choice3 and expl_choice4:
        $ expl_choice1 = False
        $ expl_choice2 = False
        $ expl_choice3 = False
        $ expl_choice4 = False
        "Так как все основные дела на данный момент были сделаны, мы решили начать выполнять собранные нами в гильдии задания"
        "Чтобы походу дела не пропустить ничего нового, Ред предложил возвращаться в гильдию. Тем самым, мы сможем сразу же отдавать новые грамоты и следить, не появилось ли новых квестов"
        jump luften_quests1
    else:
        scene bg luften2 with dissolve
    menu:
        "Найти алхимическую лавку" if not expl_choice1:
            $ expl_choice1 = True
            jump alchemist_store
        "Поискать дом на ночь" if not expl_choice2:
            $ expl_choice2 = True
            jump joseph_meeting
        "Отправиться на рынок Луфтена" if not expl_choice3:
            $ expl_choice3 = True
            jump luften_market
        "Посетить городскую гильдию" if not expl_choice4:
            $ expl_choice4 = True
            jump luften_guild

label luften_market:
    $ stage = "Рынок Луфтена"
    $ chapter = 3
    $ save_name = "Глава " + str(chapter) + ". " + stage

    show Red at center
    me "Я хотел бы сходить на рынок, думаю, там можно найти что-нибудь полезное. Сколько у нас есть денег?"
    "Ред вытащил мешочек с монетками и начал их пересчитывать. По его выражению лица я сразу прикинул, что осталось не много"
    red "Восемьдесят серебром, в принципе, что-то недорогое купить можно. Тебя свой меч устраивает кстати?"
    me "Ну, как тебе сказать... Думаю у нас на новый денег не хватит, так что да, устраивает"
    "Ред одобрительно кивнул и пошёл в сторону торговой площади. Я последовал за ним, попутно озираясь по сторонам"
    "Луфтен внутри также был необычно красив. Трудно поверить, что буквально в нескольких десятках километров от него существуют совершенно несхожие деревни"
    scene bg luften_market with fade
    "Пройдя несколько жилых кварталов, полных красивых домиков с цветами, мы вошли в длинный переулок, заполненный до отказа народом"
    "Сотни голосов то и дело доносились из лавок, десятки торговцев кричали на улице, зазывая народ. Пару раз я чуть не врезался в проходивших мимо путешественников"
    me "Ред! Куда мы идём-то? Здесь столько народу, что я боюсь, как бы не потеряться"
    "Ответа я не услышал, если бы не длинная шляпа старика, я боюсь бы так и остался стоять в переполненном переулке. К счастью, я успел пробраться в здание, куда прошёл Ред"
    scene bg alchemist_house with fade
    me "Я открыл дверь и спустился в подвальное помещение. Одного быстрого взгляда хватило, чтобы понять, что это была алхимическая лавка"
    "На удивление, внутри никого не было, даже хозяина. Только чувствовался запах табачного дыма и слышны бульканья каких-то жидкостей"
    show Red at right with dissolve
    red "Это лавка одного моего знакомого. Его зовут Диоген, он местный алхимик, торгует в Луфтене уже много лет"
    me "Тут как-то маловато народу для популярной алхмической лавки, мне кажется"
    "Голос: " "Маловато, зато когда приходят, то платят немало! Хе-хе!"
    "Из-за спины раздался хрипловатый, но суровый голос и на моё плечо упало чья-то рука"
    show Diogen at left with fade
    diogen "Рад тебя видеть, Ред. Как жизнь, как торговля? Нашёл себе нового попутчика?"
    "Передо мной оказался достаточно крепкий старик в лиловой мантии и с длинной бородой. На поясе его висели несколько колочек с жидкостью, так что догадаться о его профессии было нетрудно"
    "Старики обменялись крепкими рукопожатиями и уселись за ближайший стол, будто делают такое чуть ли не каждый день, а с их последней встречи прошло не более пары дней"
    "Я решил не вмешиваться в разговор и постоять рядом, послушать, о чём же они будут говорить"
    "Ред откинулся на спинку кресла, достал трубку и медленно закурил. Диоген просто сидел и рассматривал дубовый стол, который на самом деле был совершенно непримечательный"
    red "Жизнь так себе, денег мало, питаюсь так сказать \"хлебом с водой\". Торговля совсем ушла на второй план, да и товар давно закончился"
    diogen "И как же теперь живёшь? Тебя не было в Луфтене месяц, я слышал, ты ходил на границу с Фандером. Что ты там забыл?"
    red "Я пока не буду рассказывать, всё равно ничего не нашёл... кроме него. Его [me] зовут"
    "Ред показал Диогену на меня. Тот кивнул и, привстав, пожал мне руку. Я откланялся из вежливости и снова встал у стены"
    red "Я нашёл этого паренька у таверны на окраине Луфтена без сознания и памяти. Последние несколько дней мы потратили на поиск его родных"
    red "Побывав в трёх деревнях, мы сталкивались и с монстрами, и разбойниками. Если бы не [me], я бы ещё на тролле откинулся, ха-ха!"
    red "Но знаешь, это оказалось весьма прибыльное занятие, расхаживать по деревням и получая награды за квесты. Мне понравилось"
    diogen "Хочешь начать карьеру путешественника на старости лет? Не смеши мою бороду!"
    red "Как знать, как знать... Но это ладно, расскажи, как в Луфтене дела обстоят. Тем более [me] тоже хочет послушать"
    "Я одобрительно кивнул головой Диогену. Тот будто усмехнулся сквозь бороду в ответ и начал рассказ"
    diogen "С тех пор, как ты покинул Луфтен, начали происходить довольно неприятные вещи. В городе стало больше воров и всякого смрада"
    red "Что?! Их должны были всех переловить ещё вначале лета! Куда стража смотрит, чёрт возьми!"
    diogen "Понятия не имею, они давно уже забили на такие вещи. В городе сотни тысяч человек, тюрьмы просто переполнены"
    diogen "А они всё лезут и лезут, нескончаемый поток всякого сброда. Не в обиду вам, конечно же"
    diogen "Совет обратился за помощью к Инквизиции. Они пообещали в течение нескольких месяцев со всем разобраться, но ты же знаешь, что будет"
    red "Будет массовый геноцид магов, алхимиков и любых иноземцев! Мы через всё это проходили! Куда король смотрит?!"
    diogen "Я боюсь, он даже не знает. Или знает, но понимает, что другого выбора нет"
    diogen "Теперь ты думаю понимаешь, почему у меня больше нет клиентов. Большая часть попросту передохла"
    red "А кашу эту расхлёбывать нам... Ладно, спасибо тебе, мы не будем задерживаться"
    diogen "Понимаю. Удачи тебе, Ред, рад был снова увидеть тебя. И тебе тоже не хворать, [me]"
    "Я поблагодарил Диогена и вышел вслед за Редом из лавки на по-прежнему заполненную улицу"
    scene bg luften_market with dissolve
    "Ред молча прошёлся до ближайшей палатки с едой и купил несколько буханок хлеба и кусок мяса. Я чувствовал, что он немного не в себе"
    me "Ред, я не совсем понял из вашего разговора, кто такая Инквизиция? Это банда разбойников?"
    show Red at center with dissolve
    red "Не совсем так. Инквизиция - самая большая военная группировка в Инзеле. Но она не подчиняется ни одному из трёх королевств"
    red "Её основал и небезисвестный маг Воксен, которого изгнали из Мариэна за увлечение чёрной магией, которая официално запрещена"
    red "Оставшись без дома и знакомых, озлобленный на мир маг основал группировку и поставил себе цель - истребить всех магов и алхимиков"
    red "Скорее всего он был просто не в себе из-за своих увлечений запретными заклинаниями, но это не помешало ему найти союзников"
    red "Культ начал быстро разрастаться, но оставался подпольным, пока не произошло сожжение Деревни Ведьм"
    red "Целая деревня Мариэна, населённая магами, была уничтожена инквизицией. Это была трагедия, тысячи людей ополчились на власть"
    red "Мариэн попытался изгнать Инквизицию из королевства, но и у него ничего не вышло. И тогда все те разбойники и потянулись под крыло организации"
    red "Сейчас в группировке насчитывается более двадцати тысяч человек. Воксен, кстати, после инцидента куда-то скрылся"
    red " Вообще Инквизиция состоит преимущественно из бывших солдат, разбойников и стражи, которые по какой-либо причине отказались жить по законам своей страны"
    red "Однако, ни для кого не секрет, что их шпионы снуют практически везде, даже в тоталитарном Фандере, который, к слову, ужесточил границы именно благодаря им"
    red "За плату они готовы покрыть нелегального торговца, или же расправиться с нужными людьми. Тут уже кто больше денег даст"
    me "То есть сейчас это большая банда наёмников, которую к тому же нанял сам Император?"
    red "Они намного опасней банды. У Инквизиции очень централизованная система власти, делящая людей на ранних, подобно гильдиям"
    red "Самые нижние ранги - простые убийцы, служащие людям повыше. Те, в свою очередь, служат более высоким членам организации, и так далее"
    red "На самом верху иерархии находится верховный совет, состоящий из пяти членов. Само собой, их имена никому неизвестны"
    red "Ходят слухи, что они живут в Луфтене, но проверить такой огромный город попросту невозможно"
    red "Не совсем ясно, какая у них основная цель. Скорее всего, получение влияния, а затем и контроля над королевствами Инзеля"
    me "Разве тогда не стоит их ликвидировать? Они же прямая угроза для любой страны, а их, наоборот, нанимает власть!"
    red "Да, но их лагерь не так просто найти. Он располагается в горах Великого Хребта, те земли до сих пор толком не изведанны"
    red "Да и выгодней нанять их, чем оплачивать распоясовшиюся армию. Да, Луфтен на самом деле не такой благоухающий, как кажется на первый взгляд!"
    me "Но нужно же что-то придумать, иначе как бы и нам не попасть под горячую руку! Мы же в городе надолго"
    red "Да знаю я! Не знаю, что тут поделать. Давай уж лучше пойдём... Что там ещё у нас осталось?"
    "Мы с Редом прошли ещё раз прошли по торговой улице, и завернули назад в жилой район. Я приостановился, чтобы прикинуть, куда идти дальше..."
    jump luften_explore

label alchemist_store:
    $ stage = "Северный район Луфтена"
    $ chapter = 3
    $ save_name = "Глава " + str(chapter) + ". " + stage

    me "Давай отдадим посылку. Всё равно, Джоуна уже вряд ли найдём, а тут хоть понятно - надо лавку найти"
    "Я достал шкатулку и ещё раз осмотрел её наружность. Это было обычное дерево, с гравировкой большой буквы \"Ф\""
    me "Ф... Эй, Ред, как думаешь, что значит эта буква? Имя отправителя?"
    show Red at center with dissolve
    red "Хм, это же сосна. Скорее всего, коробка была сделана в Фандере, поэтому и гравировка мастера в честь королевства. Но это неудивительно"
    red "Фандеру для поддержания экономики просто необходимо что-то подавать на экспорт. Обычно это изделия из стали или дерева"
    me "Ну ладно, раз Фандер, то это мало что даёт. Как думаешь, где торгует этот Иоганн"
    red "Подожди... Иоганн, Иоганн... Это вроде в северной части города, в километрах пяти отсюда"
    "Ред достал из сумки набросок карты города, запачканный жирным пятнами и ткнул на его верхнюю часть своим указательным пальцем"
    red "Я думаю, нам сюда! Я раньше сам торговал в этой части города, вот в памяти и остались воспоминания"
    me "Поверю уж на слово. Давай, веди!"
    "Я и Ред направились по мостовой в северную часть города. Дорога долго извивалась в разные стороны, бесконечная череда лестниц то и дело мелькала под ногами"
    scene bg luften3 with fade
    "Мы прошли наверное метров пятьсот в высоту, прежде чем оказались в северном районе, расположенном на большой горе"
    "В концы восхождения мои ноги ныли просто ужасно. Ещё и сумка не плечах мешала всё это время, шатаясь из стороны в сторону"
    me "Давай лишний раз сюда не подниматься... Иначе мне так недолго жить останется"
    show Red at center with dissolve
    red "Не ной, я устал не меньше тебя! К тому же, мы уже почти пришли, вот та улица!"
    "Ред указал на стоявший вверху указатель своим пальцем и подтолкнул меня, чтобя я не замедлял темп восхождения"
    "Я поднялся по каменной лестнице и помог взобраться Реду. Перед нашими глазами открылась милая живописная улочка"
    me "Да... Это совсем не похоже на рынок, народу тут явно поменьше будет. Неудивительно, что ты тут ненадолго задержался, все же внизу торгуют!"
    red "Вообще-то, здесь аренда помещений раз в пять дешевле! Да и клиенты из жилых районов приходят часто, что ты сразу начинаешь, а?"
    hide Red with dissolve
    "Пока Ред продолжал ворчать на мою шутку, я прошёлся вдоль по улице. Здесь была какая-то старая булочная, кузница и таверна. И ни одной алхимической лавки!"
    me "В булочной ничего интересного, кузница, судя по вывеске на двери, сегодня вообще закрыта. Мы точно сюда пришли? А, погоди, есть же ещё вот эта..."
    "Я подошёл к большому зданию на другом конце переулка. Прямо над парадным входом красовалась большая красная надпись, сделанная гравировкой по металлу"
    me "Таверна... Иоганна? Ред, он что, переквалифицировался с алхимика на владельца гостиницы?!"
    "Ред в недоумении подошёл поближе, чтобы тоже рассмотреть сиё зрелище. Почесав свою бороду и осмотрев здание, он и сам невольно усмехнулся"
    red "Хо-хо, ну кто его знает, быть может так и есть. Это сколько же Джоун с собой посылку возил, что лавка закрылась,  а владелец таверну открыл?"
    me "Мда, надеюсь это тот самый Иоганн, а то будет как-то очень неловко, если ты что-то напутал и привёл меня не туда... Ладно, заходим"
    scene bg guesthouse2 with fade
    "Я приоткрыл дверь и зашёл внутрь зала. Внутри сидело несколько человек, дружно распивая пиво, а за барной стойкой стоял мужчина, протирая очередную кружку, оставленную клиентом"
    "Я подошёл к бармену и заказал стакан какой-то густой жидкости - самоё дешёвое, что смог найти. Через минуту заказ уже стоял на столе, а бармен снова молча начал тереть замызганную кружку своей салфеткой"
    show Host at center with dissolve
    "Бармен: " "С вас две серебряных, будьте добры"
    me "Да, сейчас будет. Кстати, не могли бы вы помочь мне с одним вопросом, сэр?"
    "Я вытащил три серебрянных монеты и положил их на стойку, чуть подвинув в сторону мужчины. Тот мигом среагировал на мою просьбу о помощи"
    "Бармен: " "Не имею права отказать, каков же ваш вопрос?"
    me "Как часто хозяин заведения здесь бывает? Я про Иоганна говорю, чьё имя есть на вывеске"
    "Бармен: " "Часто бывает, Иоганн здесь часто бывает..."
    "Бармен ухмыльнулся и сгреб плату за выпивку в мешочек, ловко подкинул его, и положил в кассу"
    me "Не могли бы вы сказать, как его проще всего найти в таком случае. Есть у меня к нему одно дело..."
    "Мне показалось будто брови бармена на мгновение нахмурились. Неужто, я что-то опять неправильно сказал?"
    "Бармен: " "Это какое же дело?"
    me "Посылка к нему у меня. На ключе, прошено не вскрывать, вот и ищу Иоганна, так как написано, что ему доставить надо"
    "Бармен: " "Гхм, раз посылка, то я могу передать. Мне не сложно, можете своё имя в конверт записать, он вам потом деньги за доставку и вернёт"
    "Бармен: " "Не ждать же вам его здесь, к тому же из-за какой-то мелочи"
    define box_given = False
    menu:
        "Передать посылку":
            $ box_given = True
            me "О, большое вам спасибо, буду очень признателен, если вы облегчите мне задачу"
            "Бармен: " "Вот и правильно. Сейчас я дам вам бумагу с чернилами, запишите всю важную информацию с помощью них"
            "Бармен дал мне письмо, чтобы я указал на нём своё имя и описал внешний вид шкатулки для подтверждения её сохранности"
            "Неуклюжим почерком я расписал очень подробно все те приметы, которые смог заметить на посылке. Из-за того, что я давно не писал, это задание оказалось весьма непростым"
            "Бармен: " "Распишитесь вот здесь, я чуть ниже. Если что случится, заходите, вы можете найти меня в любой день недели на этом же месте"
            "Поблагодарив бармена за столь приятную помощь, я опустошил кружку и кивнул сидящему за ближайшим столом Реду, что дело сделано, и можно уходить"
            scene bg luften3 with dissolve
            show Red at center
            "Отдав посылку, мы вышли из здания. Казалось бы, всё закончилось как нельзя лучше, только мне почему-то казалось, что Ред снова смотрит на меня с неким презрением!"
            me "Ну что я опять не так сделал?! Я так и чувствую на себе твой злой взгляд!"
            red "Ты доверил посылку первому встречному, даже не спросив ни имени его, ни места, где он живёт?"
            me "Нет, почему же... Ну, это же бармен заведения, хозяин которого Иоганн, которого мы и искали. Что тут может пойти не так-то? Бармен отдаст вечером посылку, и все счастливы"
            me "Я даже попросил конкретную сумму за доставку, если этот хозяин сознательный, то деньги я попросил доставить в гильдию, мы же всё равно туда рано или поздно зайдём"
            red "Ну и дурак же ты... А если бармен оставит её себе или отдаст кому-то другому?! Мы же даже не знаем что в ней! Распилят её и содержимое продадут на ближайшем рынке!"
            me "Да почему же... Ну, я надеюсь всё будет как сказал я, а не ты. Вообще, дело сделано, это уже не наша забота, не возвращаться же назад и требовать её вернуть!"
        "отказаться от предложения":
            $ box_given = False
            me "Да что вы, это совсем необязательно, я зайду попозже, лучше скажите, когда Иоганн будет, я и приду к этому времени, мне совершенно это нетрудно"
            "Бармен: " "Гхм, ну ладно, как вам угодно, моё дело предложить, выбирать всё равно только вам. Иоганн думаю будет через два дня, тогда и приходите, лучше ближе к вечеру"
            me "Так тому и быть. Ещё раз спасибо вам за питьё и помощь. Было приятно провести время, до скорого"
            "Закинув сумку на плечи, я опустошил кружку и кивнул сидящему за ближайшим столом Реду, что дело сделано, и можно уходить"
            scene bg luften3 with dissolve
            show Red at center
            "Мы вышли из здания обратно на красивую улицу северного района. После душной таверны горный воздух чувствовался особенно хорошо"
            red "Что ты узнал от бармена? Как вижу, посылка всё ещё у тебя, значит и Иоганна в таверне нет, я прав?"
            me "Ты наблюдательный. Я решил, что передам посылку лично получателю, когда тот появится. Бармен сказал, что это будет через пару дней. Так что придётся сюда ещё разок вернуться"
            red "Ну, что делать. Надеюсь внутри шкатулки лежит действительно что-топ полезное, а то неудобно выйдет, если там безделушка какая-то"
    "Внезапно я услышал за своей спиной несколько голосов, а затем шум открывающейся двери таверны"
    hide Red with fade
    show rogue2-1 at center
    show rogue2-2 at left
    show rogue2-3 at right
    if box_given:
        "Мужчина: " "Эй, ты, чем вы там с барменом обменялись, а? Поделиться с нами не хочешь? Или нам к бармену и обратиться по этому делу?!"
        "Передо мной встали трое мужчин, обнаживших ножи. Для обычных завсегдатаев таверны они выгядели уж слишком угрожающе"
        "Похоже, это те трое, что сидели в здании... Неужто они подсмотрели, как я передал шкатулку и поэтому решили стрести с меня и Реда денег за такую передачу?"
        "Даже если так, у нас их нет. Но нельзя допустить, чтобы они напали на кого-то ещё, даже на бармена. Если так дело пойдёт и дальше, беды не миновать..."
        me "Это не вашего ума дело. И не трогайте бармена, он тут совершенно ни при чём. Я не хочу вступать с вами в бой, но и ровно столько же не хочу что-либо вам рассказывать"
    else:
        "Мужчина: " "Эй, ты, что в сумке своей скрываешь, а? Поделиться с нами не хочешь, а то ты минут десять стоял, с барменом трепался!"
        "Передо мной встали трое мужчин, обнаживших ножи. Для обычных завсегдатаев таверны они выгядели уж слишком угрожающе"
        "Похоже, это те трое, что сидели в здании... Неужто они подсмотрели, как я заглядывал в сумку при разговоре с барменом?"
        "Даже если так, у нас их нет. Но нельзя допустить, чтобы они напали на кого-то еще. Они вооружены, так что если так дело пойдёт и дальше, беды не миновать..."
        me "Это не вашего ума дело. Мы просто поговорили с барменом и ушли. Я не хочу вступать с вами в бой, но и ровно столько же не хочу что-либо вам отдавать или показывать"
    me "Уберите оружие и отойдите от таверны, я не буду с вами сражаться, если этого можно избежать"
    "Мужчина: " "Ты что за херню поришь, малой? Деньги сюда быстро, пока этот нож у тебя между рёбер не оказался!"
    me "Вы сами напросились, я предупреждал"
    "Я думаю, я бы уже смог испробовать на них молниеносный удар, они явно не готовы к такой быстрой атаке"
    $ renpy.block_rollback()

    define rogue_band = None

    $ attacks = []
    $ attacks.append(attack("Трое бандитов наскакивают на вас одновременно!", std_base_attack, 40, 0))
    $ attacks.append(attack("В вас летят сразу три кинжала!", std_base_attack, 30, 0))
    $ attacks.append(attack("Бандиты нападают на вас с разных сторон!", std_base_attack, 35, 0))
    $ attacks.append(attack("Вы замечаете, что бандиты начинают вас окружать!", std_block_attack, 0, 0))
    $ attacks.append(attack("Три острых лезвия сверкнули вокруг вас!", std_base_attack, 60, 0))

    $ rogue_band = enemy("Луфтенская банда", 750, std_enemy_update, std_enemy_rand, "f")
    $ rogue_band.attacks = attacks

    $ Player = player(level, xp, std_player_update)
    $ Player.attacks.append(attack("Молниеносный удар", lightning_attack, value = Player.max_damage, cost = 2))
    if new_skill_claimed:
        $ Player.attacks.append(attack("Смертельный вихрь", tornado_attack, value = Player.max_damage, cost = 2))

    $ Log = log(std_win_check, std_lose_check, std_log_update, "Началась битва с Луфтенской бандой!")

    call screen fight_screen(Log, Player, rogue_band)

    $ newLv = Player.add_xp(300)
    $ level = Player.level
    $ xp += 300

    $ renpy.block_rollback()

    hide rogue2-1 with dissolve
    hide rogue2-2 with dissolve
    hide rogue2-3 with dissolve
    "вы получаете 300 ед. опыта!"
    if newLv:
        "Ваш уровень повышен до [level]!"
    "В действительности, слово молния, клинок мой пронёсся по телам трёх бандитов. Ещё мгновение, и они пали на мостовую, истекая кровью"
    me "Это воистину смертоносный приём, Ред. Жалко только, что пользу он приносит только вначале битвы, да и то не всегда"
    show Red at center with moveinleft
    red "В этом и суть! Учитывая сравнительно невысокую стоимость использования, он может принести большие плоды"
    red "Если нужно быстро нанести как можно больше урона из засады, то молниеносный удар подойдёт как нельзя лучше"
    red "Ах, да, ты молодец, что смог использовать его. В лесу у тебя совсем не так получалось"
    me "Видимо это так дух битвы сказался на мне. Впрочем, очень печально, что приём пришлось использовать на обычных людях"
    red "Жалея о каждом убитом злодее, добром не кончишь. Это Луфтен, тут таких навалом. Кто-то же должен с ними расправляться"
    me "Надеюсь ты прав, надеюсь ты прав..."
    "Я протёр меч и убрал его обратно в ножны. Оглянулся, поблизости никого не было, ни стражи, ни людей"
    me "Ну что же, пойдём отсюда, раз нас больше ничего не держит. Трупы придётся оставить так, нет желания таскать окровавленные тела"
    "Я вместе с Редом спустились назад в западный район Луфтена. Нам ещё предстояло выполнить немало дел"
    jump luften_explore

label joseph_meeting:
    $ stage = "Особняк Йозефа"
    $ chapter = 3
    $ save_name = "Глава " + str(chapter) + ". " + stage

    me "Теперь не помешает найти дом на ночь. Тут точно должна быть какая-нибудь недорогая таверна"
    show Red with dissolve
    red "Таверна? Не смеши меня, [me], ты правда думал, что мы будем снова ночевать в обычной грязной таверне? Мы же в Луфтене!"
    me "Не совсем понимаю, к чему ты клонишь... У нас до сих пор нет денег на снаряжение, а тем более на нормальную комнату!"
    red "Скоро увидишь. Пошли за мной!"
    hide Red with moveinbottom
    "Ред чуть ли не бегом отправился в сторону южного района города. Этот старик был бодр как никогда прежде!"
    me "Да куда же мы идём, меня хоть подожди! Не забывай, практически все вещи на {b}моих{/b} плечах лежат!"
    scene luften_square with dissolve
    "Быстрым шагом мы миновали городскую площадь и толпы народа, затем свернули по аллее в нижнюю часть города. Эти места были намного красивее, чем я представлял"
    scene joseph_house1 with fade
    "Пройдя несколько сотен метров, я заметил, как сильно преобразился Луфтен. Тут уже не было тех грязных и обшарпанных домов - только красивые особняки"
    "Мы шли по мощёной новым каменным кирпичём улице, мимо элитнейших участков и садов. Каждый дом казался мне невообразимо величественным, и я просто не успевал переключать свой взгляд с одного на другой!"
    me "Ред, что это за место? Зачем нужно было чуть ли не силой тащить меня сюда?"
    me "На этой улице только частные дома, нет ни таверн, ни гостиниц, или же..."
    show Red with dissolve
    red "Или же у меня есть друзья, которые могут нас приютить. Сейчас проверим, дома ли старина Йозеф!"
    "Ред остановился у трёхэтажного кирпичного дома и, открыв стальную калитку, зашёл на территорию поместья"
    "Я медленно проследовал за ним по каменной тропинке, словно ручей петлявшей между клумбами"
    red "Эй! Есть кто дома? Это я, Ред, пришёл в гости к Йозефу, он откроет же своему другу?"
    "На окне второго этажа показался мужской силуэт"
    "Голос: " "Откроет, заходите внутрь через входную дверь, там не заперто"
    "Я подошёл к двери и приоткрыл её. Из знания мне в ответ подул лёгкий ветерок"
    red "Ну не стой столбом, там нет монстров, заходи внутрь!"
    "Я переступил порог особняка. Почему мне показалось, что оттуда исходит опасность? Больное воображение?"
    scene joseph_house2 with dissolve
    "Зайдя внутрь, я удивился красоте и таинственности этого удивительного здания. Мы оказались в большом двухэтажном холле, с кучей мебели и декораций"
    "В углу стояла статуя какой-то человеческой фигуры, на полу лежал явно не дешёвый ковёр"
    "Слева от входа располагался коридор, уходивший на веранду, а справа - покрытая лаком дубовая лестница, ведущая на второй этаж здания"
    "Несколько голов диких животных висели на стенах, начиная от оленя и заканчивая то ли медведем, то ли волком"
    "Пока я изумлялся ранее не виданной мною красоте, сверху раздался шум запог об паркет - к нам спустился человек в нарядной форме"
    show Joseph at center with fade
    joseph "Добрый день господа, добро пожаловать в моё скромное поместье!"
    "Уже поседевший человек в позолоченном зелёном жилете и красном плаще явно был хозяином такого дома, это чувствовалось с первого взгляда"
    "Движения его были плавны, а выражение лица распрострянала неподдельную доброту и дружелюбие. Все мои опасения как ветром сдуло"
    "Встав посреди комнаты, мужчина протянул руку Реду, однако я подметил, что краем глаза он смотрит на меня"
    joseph "Ред, очень рад, что ты в кое-то веки удосужился навестить старого друга. Я уж думал, что ты совсем забыл, с кем когда-то проводил вечера за пачкой игральных карт в каком-нибудь..."
    show Joseph at left with moveinright
    show Red at right with moveinright
    red "Давай сейчас не будем об этом вспоминать. Я тоже рад тебя видеть, Йозеф. Очень сожалею, что удаётся навещать тебя, только когда от тебя что-то требуется"
    "Лицо Йозефа помутнело, а брови опустились вниз. В одно мгновение мужчина преобразился до неузнаваемости"
    joseph "Только не говори, что ты опять кому-то задолжал деньги. Я уже устал за тебя платить!"
    red "Что?! Нет, ты меня неправильно понял! Всё в порядке, я расплатился со всеми кредиторами, даже смог отыскать подручных Георга, чтобы отдать ту сумму..."
    red "В общем, дело уже закрыто, все живы и здоровы. Я пришёл совершенно по другому поводу - нам нужен дом, где мы бы могли остановится, пока пребываем в Луфтене"
    "Услышав заветные слова, Йозеф снова принял свой обычный весёлый вид, будто ничего такого и не случилось"
    joseph "А, хотите у меня пожить некоторое время? Это без проблем... О, кстати, как вас зовут, уважаемый знакомый моего наилучшего друга, Реда Англауса?"
    me "Я... Меня [me] зовут, я путешествую с Редом последнюю неделю. Долгая история, если начать с самого начала рассказывать"
    joseph "Ничего страшного, я думаю у нас много свободного времени... Вы наверное кстати голодные! Давайте я накрою на стол в беседке, вы пока подождите здесь"
    "Йозеф взял небольшой сундук, стоявший у двери и удалился во двор. Я, растерянный, остался стоять с Редом посреди огромной комнаты поместья"
    hide Joseph with fade
    show Red at center
    me "И... Что это было? Ред, теперь у меня к тебе ещё больше вопросов. Я-то думал, что начал тебя хоть немного понимать..."
    red "Не буду я отвечать на твои глупые вопросы. Йозеф - мой старый друг, мы с ним познакомились лет десять назад. Если что узнать надо - его и спрашивай"
    "Видимо я случайно потревожил не самые приятные воспоминания Реда. И по видимому, действительно лучше не затрагивать эту тему в разговоре с ним"
    red "Я пойду посмотрю, как там Йозеф, он должен был уже накрыть на стол. Ты тоже оставь сумку здесь и выходи в сад. Наконец-то хоть нормально поедим"
    hide Red with dissolve
    "Ред бросил сумку у двери и быстрым шагом вышел через парадную дверь во двор"
    me "Ну и характер! Ну ладно, друзей не выбирают, пойду чтоль и я в эту беседку. Всё равно, кушать больше всего сейчас хочется"
    scene bg joseph_house1 with dissolve
    "Также оставив вещи, я вышел из дома. В действительности, посмотря вправо, в глаза бросилась маленькая деревянная постройка, внутри которой две фигуры копошились с тарелками и скатертью"
    show Joseph at left with dissolve
    show Red at right with dissolve
    joseph "А вот и наш друг [me] пожаловал! Проходи, не стесняйся, садись за стол! Я тут вам вишнёвых рулетиков из местной булочной достал, они свежайшие, их вкус словами не опишешь!"
    "Выслушав поистине уникальную речь Йозефа о ягодных булочках, я уселся за стол и подвинул к себе чашку с чаем. Было очень трудно удержаться и не накинуться сразу на всю стоявшую на столе еду"
    joseph "Ну что, рассказывайте, где вы были, как оказались в Луфтене в такое неспокойное время? Ред, я слышал, ты ездил к северной границе?"
    red "Было дело. Правда, в Фандер я попасть так и не смог. Эта пограничная стража совсем уже  распоясалась! Пришлось тащиться назад"
    red "Своего товарища я встретил прямо на дороге. Он как с неба свалился, причем совершенно не помнил ни кто он, ни откуда, только своё имя"
    red "Но [me] оказался на удивление способным. С его помощью мы разгромили банду разбойников, он спас деревню от троллей, а ещё уничтожил кабана, который..."
    "Ред на мгновение замолчал, будто поперхнулся. Я хотел было помочь ему, но он дал знак, что всё в порядке"
    red "Йозеф, ты знаешь, на что это может быть похоже?"
    "Ред достал из под плаща кусок каменной кожи кабана и положил на стол. Йозеф с удивлением наклонился и начал рассматривать трофей"
    joseph "Это... Это же не просто камень, я прав? От него до сих пор исходит заряд магической энергии. Ред, расскажи, кого вы встретили и где?!"
    red "Это был огромный монстр-кабан из камня, как бы нелепо это не звучало. Мы встретили его у деревни Криа. Все жители оттуда странным образом исчезли, а само место осталось заброшенным"
    red "Если бы не [me], боюсь это чудище бы в миг уничтожило нас. Пришлось дать парню одно зелье для увеличения сил, ты бы знал, сколько оно стоило..."
    joseph "Много. Просто удивительно, что вы ещё в живых. Если от всего лишь его кожи исходит такой заряд маны, то боюсь представить какого было тем, кто встретил эту штуку в расцвете её сил"
    joseph "И самое главное, её создатель должен быть одним из сильнейших магов Инзеля, вы обязательно должны сообщить об этом монстре гарнизону!"
    me "Мы хотели это сделать, просто ещё не успели. Это одна из наших приоритетных задач"
    "Йозеф замолчал на несколько минут, медленно сел на стул и задумался"
    joseph "Ладно, сделаете это завтра, я думаю вы и так устали после такой дороги. Можете отдохнуть у меня некоторое время"
    joseph "Я пойду к себе, мне надо многое обдумать"
    "Йозеф медленно поднялся из-за стола и пошёл по лужайке в сторону дома, оставив нас с Редом снова одних"
    hide Joseph with fade
    show Red at center
    red "Как ты заметил, Йозеф местами очень вспыльчивый. Но ты его за это не вини, характер человека не так просто исправить"
    "Я отхлебнул чая из фарфоровой чашки и закусил это куском вишнёвого рулета. Мы просидели в тишине до самых сумерек, пока вся еда не было съедена"
    red "Я познакомился с Йозефом, когда мой бизнес переживал свои худшие времена. Я торговал всякими безделушками, не имея специальности, поэтому и спрос был невелик"
    "Ред ни с того, ни с сего начал рассказывать о былых временах. Пользуясь моментом, я в свою очередь начал внимательно слушать"
    red "У меня скопилось много долгов, за аренду, за товар, за проигранные партии в картах... И тогда появился Йозеф, будто из ниоткуда, и помог мне"
    red "Он сказал что-то вроде: \"Потрать деньги с умом\". Я и попытался. В конечном итоге, вышел в ноль - остался без лавки, денег и еды. Только сумка, ржавый меч, да пара драгоценных камней"
    red "После этого я долго занимался нелегальной торговлей, в том числе доставляя зелья в Фандер. Меня чуть не упекли в тюрьму, но по подделанным жетонам гильдии удалось скрыться"
    red "Я как раз и пытался доставить то зелье, которое ты использовал в битве с кабаном. Оно стоило кучу денег, но через границу в этот раз меня не пропустили"
    red "Оно стоило мне моих последних сбережений... Если бы не ты, [me], я бы остался без ничего, кое-как прожил бы пару недель и откинулся. Наверное, даже до Луфтена в одиночку бы не добрался"
    red "Я поступил эгоистично, да. Я знал, что ты сможешь своими силами раздобыть денег, которых бы хватило нам обоим. Под предлогом поиска твоих родных я заставил тебя драться с монстрами, людьми..."
    red "Прости меня, я правда не хотел ничего такого. Просто, сам понимаешь, каждый хочет иметь крышу над головой, еду, людей, которые бы ему помогли. Особенно на старости лет"
    me "Ред... Ты ни в чем не виноват! Наоборот, без тебя я бы никогда не смог оказаться в таком месте, как это! Ты всё это время был для меня наставником, учителем, а сейчас говоришь такое... Как так можно?!"
    red "Правда так думаешь?"
    "Монолог Реда тронул меня до глубины души. Даже, если всё это было чистая правда, какая к чёрту разница? Я бы никогда не достиг ничего без его помощи"
    me "Да, я так думаю! Так и есть!"
    "Лицо Реда озарилось лёгкой, еле заметной улыбкой. Он привстал, надел шляпу себе на голову и молча зашагал в сторону особняка"
    hide Red with dissolve
    me "Эй, что это значит?"
    "Я прокричал вслед старику, но тот даже не развернулся в мою сторону. Только пройдя до самой двери, он крикнул мне, стоявшему в недоумении:"
    red "Я пойду спать, и тебе советую! Завтра нас снова ждёт нелёгкий день, отоспись наконец как следует"
    "Шляпа старика скрылась внутри тёмного зала, и я остался совершенно один в потемневшем ночном саду. Тут было так приятно, даже уходить не хотелось"
    me "Поспать что ли прямо здесь? В сумке остался кусок ткани, который мы использовали как палатку пару дней назад... Или когда это там было?"
    scene bg black with dissolve
    "Рассуждая сам с собой, я невольно улёгся на траву и задумался, смотря на ночное звёздное небо. Это было уже не то небо, которое я видел близ деревни Красного Дуба, нет"
    "Чувствовалось, что это не поле, вдали больше не стрекотали кузнечики, их пронизывающие звуки заменились на стук повозок по мостовой, на ржание лошадей и отдалённые возгласы людей с рынка"
    "Это был Луфтен, столица королевства. Только подумать, я, будучи практически никем, добрался до сюда! И теперь лежу на траве в саде графа, рядом с трёхэтажным особняком!"
    "Вскоре такие мечты и грёзы привели меня в сон. Ещё мгновение - и все мои мысли рассеялись, я погрузился в сладкую дрёму"
    "..."
    joseph "Я смотрю, ты неплохо тут устроился? Что, на свежем воздухе спится легче!"
    scene bg joseph_house1 with fade
    show Joseph
    "Громкий голос раздался прямо надо мной, отчего я даже подпрыгнул. Сон развеялся за долю секунды"
    me "А? Я? Да... Доброе утро, Йозеф, простите, что не принял ваше приглашение поспать дома, я просто лёг и..."
    joseph "Ой, да не бери в голову! Я встречал самых разных чудаков, и многие оказывались весьма интересными и хорошими людьми"
    "Йозеф стоял передо мной со шпагой за своим поясом. Одет он был как и раньше, не считая новых блестящих сапог"
    me "Уже светло... Сколько сейчас времени? Я наверное заспавлся, давно не было времени как следует отдохнуть"
    joseph "Десять утра. Но Ред ещё спит, он сказал до полудня его не будить. Я бы и тебя не стал, только вот ты спишь на поляне, где я обычно тренировки провожу"
    "Я встал и убрал самодельный спальный мешок в свою сумку. К сожалению, она была вся промокшей из-за росы"
    me "Вы занимаетесь фехтованием? Я бы и никогда не подумал, что такой..."
    joseph "Что такой граф, как я, не может драться на мечах? Хо-хо, может твои догадки и применимы к большей части Луфтена, но точно не ко мне. А я смотрю, и у тебя меч есть"
    "Йозеф указал пальцем на меч, лежавший поодаль от сумки на влажной траве. Видимо, он отцепился случайно, когда я вставал"
    me "А, да, тоже приходится. Ред же вам говорил, что я с монстрами сражаюсь. Не то чтобы мне это нравилось, но жизнь право выбора не даёт"
    joseph "Ты зря так говоришь. Бой на мечах - это искусство, это красота, не сравнивая ни с какой картиной или скульптурой"
    joseph "Ни одна рука мастера не может передать в своей работе ту динамику, тот накал страстей, который чувствуется во время схватки"
    joseph "Сражаясь, сердце твоё должно пылать, а разум быть холодным, как лёд. Только тогда ты почувствуешь это прекрасное чувство"
    "Йозеф скорее всего прав, я чувствовал что-то подобное, доли секунды, но я помнил! Неужели это и есть тот накал?"
    joseph "Эй, [me], хочешь дуэль между мной и тобой? Я почту за честь сражаться с таким как ты"
    me "Что? Дуэль? С вами, сэр Йозеф?!"
    joseph "Именно. Ты не думай, мы не будем сражаться до смерти, никто не пострадает. Это будет всего лишь небольшой показательной тренировкой"
    "Йозеф предлагает мне сразиться на мечах... Имею ли я вообще право отказаться от неё? Ну что же, раз решаю я, то..."
    menu:
        "Принять вызов":
            me "Хорошо, я принимаю вызов, сэр Йозеф!"
            joseph "Превосходно. В таком случае будем сражаться на наших обычных мечах, если не возражаешь"
            joseph "Как только кто-либо будет слишком сильно ранен, дуэль будет окончена, а все разногласия забыты, идёт?"
            me "Идёт, начинаем!"
            "Я подобрал меч и встал с ним а пяти метрах от Йозефа. Граф же достал из-за пояса шпагу и, пригнувшись, направил её на меня"
            joseph "Пусть этот бой запомнится нам с тобой надолго!"
            me "Я бы мог попробовать использовать приём, которому меня обучил Ред... Хотя, в этом мало смысла, Йозеф вряд ли будет не готов к такому. Придётся действовать своими силами"
            $ renpy.block_rollback()

            define joseph_duel = None

            $ attacks = []
            $ attacks.append(attack("Йозеф делает прямой удар своей шпагой!", std_base_attack, 40, 0)) #base
            $ attacks.append(attack("Йозеф делает выпад вперёд, выставив свою шпагу!", std_base_attack, 45, 0)) #base
            $ attacks.append(attack("Йозеф парирует вашу атаку!", std_base_attack, 50, 0)) #base
            $ attacks.append(attack("Йозеф приготовился к атаке...", std_block_attack, 0, 0)) #block
            $ attacks.append(attack("Йозеф делает комбинацию из пяти ударов!", std_base_attack, 85, 0)) #after-block
            $ attacks.append(attack("Йозеф встаёт в в защитную стойку и выжидает...", std_wait1_attack, 0, 0)) #wait
            $ attacks.append(attack("Йозеф атакует своим самым сильным приёмом!", std_wait2_attack, 100, 0)) #after-wait

            $ joseph_duel = enemy("сэр Йозеф", 900, std_enemy_update, std_enemy_rand)
            $ joseph_duel.attacks = attacks

            $ Player = player(level, xp, std_player_update)
            $ Player.attacks.append(attack("Молниеносный удар", lightning_attack, value = int(Player.min_damage * 0.5), cost = 2))

            $ Log = log(duel_win, duel_lose, std_log_update, "Началась дуэль с сэром Йозефом!")

            call screen fight_screen(Log, Player, joseph_duel)

            $ duel_won = Player.health > 0

            $ newLv = Player.add_xp(500)
            $ level = Player.level
            $ xp += 500 #2000 / 2100 | default: 1500 / 2100

            $ renpy.block_rollback()

            if duel_won:
                "Вы получаете 500 ед. опыта!"
                if newLv:
                    "Ваш уровень повышен до [level]!"
                "Я наношу финальный удар, и Йозеф падает на колени. Увидев знак в виде его поднятой руки, я убираю свой меч"
                joseph "Это было невероятно... [me], у тебя явно есть талант, иначе и быть не может. Ты победил меня, Йозефа, а это чего-то, да стоит!"
                "Я помог Йозефу подняться с земли и отряхнуть пыль. К счастью, ни у кого из нас серьёзных ран не было"
                me "Должен признаться, победа в битве далась мне нелегко. Я благодарен вам, за то, что дали возможность поучаствовать в дуэли"
            else:
                me "Я упал на влажную траву, прикрывая истекающую кровью рану. Йозеф помог мне встать и предложил помочь перебинтовать место удара"
                joseph "Извини меня, если что. Согласен, бой был не совсем равным, но ты держался очень даже неплохо"
                joseph "Местами мне даже казалось, что я сейчас окажусь в безвыходном положении, но волей обстоятельств все закончилось в мою пользу"
                "Я привстал и смахнул со своего лица пыль и капли пота. Йозеф же дал мне лечебное зелье, чтобы рана зажила быстрее"
                me "Ничего страшного, я не сержусь ни за что. Это была хорошая битва, во всяком случае я её запомню надолго..."

        "Отказаться от дуэли":
            me "Извините, Йозеф, но боюсь не в этот раз. Дуэль будет бессмысленна, пока мой опыт владения мечом столь мал"
            me "Может быть однажды, когда я наберусь достаточно сил, я с радостью приму этот бой, но сейчас я у нему не готов"
            "Йозеф с некоторыми сожалением повернул голову и посмотрел куда-то в сторону. Это вряд ли был тот ответ, которого он ожидал"
            joseph "Может ты и прав, [me], быть может ты и прав. В таком случае я пока потренируюсь здесь, а ты можешь что-нибудь из этого подчерпнуть"
            me "Обязательно так и сделаю! Мне есть много чему учиться, особенно у вас!"
            "Пока Йозеф тренировался, я молча сидел на скамейке и смотрел за его мощными и в тоже время грациозными ударами шпаги"
            "Оружие его то и дело мерцало, а затем возвращалось в исходное положение, словно никогда его и не меняло"
            "Это действительно было искусство, пока мне неподвластное"

    me "Вне сомнения, ваше мастерство во владении мечом неподражаемо, Йозеф. Я и близко не стою рядом с вами"
    "Йозеф убрал шпагу и протёр своё мокрое от пота лицо платком из кармана"
    joseph "Глупости, я ещё очень далёк от совершенства. Видел бы ты сэра Штрауфа или Дина!"
    me "Кого? Ой, то есть, извините, Йозеф, не могли бы вы рассказать мне немного о мире, я же потерял память неделю назад"
    joseph "Рассказать о мире? Ну, я в принципе могу, если есть какие-то вопросы - можешь смело задавать"

label joseph_talk:
    if not (ask_counter1 and ask_counter2 and ask_counter3 and ask_counter4):
        menu:
            "расскажи о рыцарях Инзеля" if not ask_counter1:
                $ ask_counter1 = True
                me "Йозеф, ты упомянул сэра Штрауфа, и на самом деле это имя я уже слышал от Реда. Так что же это за человек?"
                joseph "О, ты не слышал о четверке величайших рыцарей Инзеля? Ну тогда тебе повезло, сейчас Йозеф разложит для тебя всё по полочкам!"
                "Йозеф присел на скамейку и начал свой рассказ..."
                scene bg dead_lands1 with dissolve
                show Shtrauf
                joseph "Сэр Штрауф - главнокомандующий армии Луфтена и глава городской гильдии, один из её бриллиантовых членов"
                joseph "Этот воин уже много лет служим императору Луфтена, став чуть ли не членом королевской семьи. Получив такую известность, одна из его особенностей не могла остаться без внимания..."
                joseph "Штрауф Является одним из сильнейших воинов Инзеля и, ко всему прочему, обладает уникальным артефактом, подаренным Эрлихом после победы над пламенным драконом"
                joseph "Эта реликвия наделила рыцаря невиданной силой - зачарованием оружия без использования маны, что, как ты наверное знаешь, не подвластно ни одному смертному"
                joseph "Никто точно не знает, как устроен этот артефакт, но ясно одно - тот, кто обладает им, становится практически непобедимым"
                me "Таинственный артефакт? Это какая-то мощная магическая штуковина, не имеющая аналогов?"
                joseph "Типо того, только артефактов несколько. Про них я мало знаю, лучше спроси Реда. Это очень скользкая тема, если честно..."
                "Йозеф решил не давать чёткого ответа, что весьма странно. Ну ладно, видимо он действительно не разбирается в этой теме"
                me "А что насчёт, как его... Дина? Это тоже обладатель артефакта?"
                scene bg castle1 with dissolve
                show Din
                joseph "Нет, Дин как раз таки им не обладает. Но это не делает его менее запоминающейся личностью!"
                joseph "Дин - полководец Фандера и один из защитников Имера IV. За его сокрушающие удары на поле боя его даже прозвали \"рыцарем грома\". Вот как сильно враги разлетались!"
                joseph "Этот рыцарь уже много лет возглавляет военную гильдию Фандера, а также руководит имперскими отрядами в Фандере, включая даже самых элитных"
                joseph "Как и Штрауф, Дин находится в очень тесных связях с королём, и если бы не законный наследник, Имер V, то после смерти нынешнего правителя Дин вполне смог бы занять место на троне"
                joseph "Самое удивительное, что он достиг такого чина и мастерства, по сути не обладая никакими магическими иоли иными способностями, а лишь своим мастерством"
                joseph "Вот такой человек и будет поистинне уникальным. Представляешь, сколько людей вдохновилось им, сколько начало свою карьеру воинов благодаря ему!"
                scene bg joseph_house1 with dissolve
                show Joseph at center
                jump joseph_talk
            "Расскажи мне побольше о Реде" if not ask_counter2:
                $ ask_counter2 = True
                me "Йозеф, не мог бы ты рассказать мне о ваших взаимоотношениях с Редом. Я, как понял, ты всячески помогал ему в трудные времена?"
                joseph "Да, было дело, пришлось его и выручать материально. Он ввязался в опасную игру, и задолжал немало денег одной группировке..."
                me "Группировке? Какой?"
                joseph "В Луфтенском порту уже много лет заправляют различные торговые объединения. Они заправляют заведениями, скупают товар, дают в аренду корабли"
                joseph "И само собой, дают денег в кредит. Ред сделал глупость тогда, решил набрать денег, а вернуть не смог. Представь какая охота за его головой тогда началась!"
                joseph "Всё бы ничего, но это была организация под контролем Георга Таинственного, самого влиятельного торговца Луфтена, а может и всего мира"
                me " Почему этого Георга зовут таинственный?"
                joseph "Потому что лица его никто не видел. Не знаю как, но он уже несколько лет управляет своей организацией, при этом никому не показав своего лица"
                joseph "Конечно, такой человек не может нравится властям столицы, но поймать его пока никто не решился, да и не нужно это"
                joseph "За мою жизнь в Луфтене город преображался много раз, и большее влияние на это оказывали именно такие торговые организации, как у Георга"
                joseph "И скажу прямо - сейчас столица выглядит на порядок лучше, чем когда-либо ещё"
                "Я слышал самые разные мнения об этом городе. Хм, видимо, действительно, тут все не так просто"
                jump joseph_talk
            "Кто такой Цвайн?" if not ask_counter3:
                $ ask_counter3 = True
                me "Я слышал от Реда об одном из великих рыцарей, краем уха. Его Цвайн звали. Мне кажется, или никто почему-то никогда о нем не говорит?"
                joseph "Цвайн?.."
                "Лицо Йозефа потемнело, а с лица сошло хоть малейшее проявление улыбки"
                joseph "Ты же ничего о нём не знаешь, так?"
                me "Нет, ничего, только Ред упомянул его, когда рассказывал о битве с пламенным драконом. А что с ним? Где он сейчас?"
                joseph "Понятия не имею. Слушай, [me] не лезь в это дело, правда. В Инзеле есть вещи, о которых не стоит даже говорить..."
                me "Но... Я даже не понимаю, в чём дело! Как же мне..."
                joseph "Вот и хорошо, что не понимаешь. Закрыли эту тему, я не буду отвечать на такой вопрос. И Реда тоже о нём не спрашивай"
                "Йозеф отказался давать какие-либо объяснения, и мне ничего более не оставалось, как перевести тему разговора"
                jump joseph_talk
            "Научи меня приёму" if not ask_counter4:
                $ ask_counter4 = True
                me "Йозеф, не могли бы вы... Как бы сказать... Научить меня какому-нибудь новому приёму"
                joseph "Приёму? В плане?"
                me "Понимаете, я ещё совсем не опытный во владении меча, а следственно - бой мой весьма примитивен. Если бы я знал больше техник"
                joseph "Ааа, понял! Думаю да, я смогу тебя научить одному приёму, который я и сам использую"
                me "Это было бы просто чудесно! Как же он называется?"
                "Йозеф смутился, будто мой вопрос застал его врасплох"
                joseph "Лучше бы спросил, как он исполняется. Ну, впрочем, ладно. Его имя - смертоносный вихрь, как тебе такое?"
                me "Звучит... Смертоносно. Как его использовать?"
                joseph "Этот прием можно исполнить почти в любое время боя. Тебе нужно быстро принять стойку, а затем нанести несколько ударов, не опуская меч"
                "Йозеф вытащил шпагу, чтобы показать мне, как проводить серию приёмов. Пригнувшись, он сделал первый замах..."
                show Joseph with fade
                "Несколько вспышек пролетело слева от меня, словно искры. Своей шпагой Йозеф нанёс несколько ударов буквально за секунду!"
                me "Вау, это было невероятно. Йозеф, не могли бы вы повторить его ещё пару раз, чтобы я как следует разглядел?"
                joseph "Без проблем, у меня ещё достаточно сил для этого!"
                "И вот взмахи снова засверкали в утреннем воздухе, и я снова почувствовал ту силу, которая исходила от Йозефа"
                joseph "Как-то вот так.  Теперь попробуй сам!"
                me "С моим-то мечом... Ну, ладно, попытка - не пытка"
                show Joseph at right with moveinright
                scene bg joseph_house1 with fade
                show Joseph at right
                "Я заношу свой меч и делаю несколько медленных, неуклюжих ударов, а затем с грохотом роняю оружие на землю"
                me "Это... очень трудно, мой меч с десяток кило весом, как же мне им управлять?"
                joseph "Ничего! Главное - держи центр тяжести. Управляй им, стараясь двигаться вместе с мечом!"
                "Это легко сказать. Потратив ещё пару попыток, я смог сделать только два удара подряд, да и то, затратив на это слишком много времени"
                joseph "Уже неплохо! Попробуй ускорить свои атаки, помни - чем дольше ты удерживаешь меч в воздухе, тем больше устаешь. Всё должно происходить за мгновение!"
                me "Ну-ка, удар!"
                scene bg joseph_house1 with fade
                show Joseph at right
                "Несколько мощных ударов, словно гром, разразились передо мной. Тяжело дыша, я воткнул меч в землю"
                me "У меня... У меня получалось?"
                joseph "Да! Отлично, [me], это то, что я и имел ввиду! Немного практики, и ты точно сможешь овладеть этим приёмом!"
                me "Вы правда так думаете?"
                joseph "Конечно же! Я не прогадал, внутри тебя действительно есть зачатки таланта, [me]"
                "Изучен новый приём: \"Смертносный вихрь\"!"
                "Я вытащил меч и убрал его в ножны. Йозеф помог мне отряхнуться от земли, и ещё раз похвалил за успехи"
                $ new_skill_claimed = True
                show Joseph at center with moveinleft
                jump joseph_talk

    show Joseph at left with moveinleft
    show Red at right with moveinright
    $ ask_counter1 = False
    $ ask_counter2 = False
    $ ask_counter3 = False
    $ ask_counter4 = False

    red "Утро доброе вам, [me], Йозеф, что делаете?"
    joseph "Тренировались. Твой друг делает успехи, ты знаешь?"
    red "Догадываюсь. Но знаете, уже за полдень, и я думаю, нам пора идти. Я оставлю часть вещей здесь, надеюсь к вечеру вернёмся"
    joseph "Без проблем, буду ждать вашего прихода. В случае чего - дом всегда в вашем распоряжении"
    "Йозеф протянул Реду ключ от входной двери, а затем о чём-то с ним переговорил. Старик кивнул и позвал меня к выходу из сада"
    if duel_won:
        joseph "О, ещё кое-что, [me]. Как подарок за ту превосходную битву между нами, я бы хотел тебе кое-что подарить"
        "Йозеф протянул мне маленький золотой ключик на цепочке, украшенный драгоценным камнем"
        joseph "Как талисман на память или удачу. Кто знает, вдруг пригодится"
        me "Спасибо вам, Йозеф, спасибо за всё ещё раз"
    hide Red with dissolve
    hide Joseph with dissolve
    "Ред и я вышли из сада и направились обратно по мостовой в центр города. Сегодняшнее утро выдалось особенно жарким, но сейчас это не особо меня смущало"
    jump luften_explore

label luften_guild:
    $ stage = "Гильдия Луфтена"
    $ chapter = 3
    $ save_name = "Глава " + str(chapter) + ". " + stage

    me "Я думаю, сейчас стоит сходить в гильдию. Ты сказал, что там можно получить новые задания"
    red "Именно так. Ещё неплохо бы сдать все те накопленные грамоты, за них нам дадут хотя бы бронзовый ранг"
    me "В таком случае - веди. Уже не терпится найти пару-тройку интересных квестов с хорошей наградной!"
    "Ред повёл меня по главной улице прямо в центр города. Постепенно округа становилась всё шумнее и шумнее, а потом голоса людей прерватились в ужасный гул"
    scene bg luften_square with dissolve
    "Мы вышли на огромную площадь, усыпанную маленькими, как муравьи, людьми. Повсюду слонялись торговцы, проезжали экипажи, бегали рыцари"
    me "Ничего себе! Здесь словно собрались все жители Инзеля, как же много народа..."
    show Red at center with dissolve
    red "Однако, его стало меньше с момента моего ухода. Помню раньше сюда даже протиснуться было нельзя, а теперь что?"
    me "Мне кажется, ты мыслишь пессимистично, Ред"
    hide Red with dissolve
    "Пока мы пробирались сквозь толпу, я начал слышать чей-то громкий и отчаянный голос. Дёрнув Реда за рукав,я решил остановиться и прислушаться"
    "На другом конце площади, на возвышении, стоял рыцарь, подымающий то и дело свой меч вверх. Вокруг него толпилась куча народа и несколько стражников, пытавшихся предотвратить давку"
    "Как только я подошёл на расстояние в десять метров, я смог различить те слова, которые доносились из под его забрала. По видимому, этот человек не особо хотел показывать своё лицо"
    show gold_knight with fade
    "Рыцарь: " "Граждане Луфтена! Граждане Луфтена, очнитесь! Разве вы не видите, что происходит вокруг нас?! Сколько можно терпеть этот произвол, этот сброд, что населяет теперь наш город?!"
    "Рыцарь: " "Каждый день умирает всё больше и больше невинных людей! И всё почему?! Потому, что наш король, уважаемый Эрлих II, давно позабыл о своём народе!"
    "Рыцарь: " "Страже давно наплевать, что происходит в городе, наша некогда прекрасная столица погрязла в хаосе и разрухе! Как такое могли допустить нынешние власти?!"
    "Рыцарь: " "Уже больше нет правосудия, кто виноват, а кто нет - судит какая-то банда разбойников, и король это поощрает! В этом королевстве больше не осталось правых воинов, оно погрязло в коррупции, взяточничестве и жадности!"
    "Рыцарь: " "Так очнитесь же от этого сна! Оглянитесь вокруг, посмотрите, что стало с нашим домом! Посмотрите..."
    "Передо мной появился Ред и заслонил сцену, на которой выступал рыцарь"
    hide gold_knight with fade
    show Red at center
    red "Пойдём, [me], не вижу смысла слушать эту речь"
    me "Эй, почему? Мне же интересно узнать, о чём говорит этот воин..."
    red "Простыми словами здесь ничего не изменишь, да и бесполезно пытаться внушить этим безмозглым дворянинам или торговцам, что надо что-то менять"
    red "Большинство населения Луфтена прежде всего будут думать о своей собственной шкуре, а не во всеобщем благе. Так что давай не будем встревать в эту историю"
    "Ред явно не хотел, чтобы я дослушал эту речь до конца, так что я не стал сопротивляться и пошёл далее в сторону большого собора на противоположной части центральной площади"
    scene bg guild_hall1 with dissolve
    "Мы прошли сквозь покрытую золотом арку внутрь величественного, залитого лучами полуденного солнца, зала. Помимо нас внутри было ещё много самых разных солдат, торговцев, рыцарей"
    show Red at center with dissolve
    red "Это - зал городской гильдии. Сюда и приходят все путешестевенники и послы из деревень, чтобы обменяться заданиями. Впрочем, я думаю, ты ещё помнишь об этом, я рассказывал"
    me "Да, прекрасно помню. Просто... Это место поистинне потрясающе! Я никогда ещё не видел такого монументального и красивого произведения архитектурного искусства!"
    red "Да, место действительно впечатляет. Ты можешь здесь осмотреться, однако у нас есть дела, не забывай"
    hide Red with moveinright
    "Ред направился в сторону досок с объявлениями, оставив меня осматривать основной корпус. К счастью, здесь было, чем заняться"
    "Недолго думая, я подошёл к ближайшему из здешних посетителей и попытался завести разговор. Участь моего собеседника выпала одному из рыцарей в красной одеянии"
    show knight1 with dissolve
    me "Какой прекрасный денёк, не находите?"
    "Произнеся эти банальные слова, я уселся на скамью рядом с воином, полировавшим на данный момент свой старый длинный меч и смотревшим куда-то вдаль"
    "Рыцарь: " "Ты кто такой? Не видишь, я работой занят, чего пристал?"
    me "Я - путешественник, начинающий воин и просто хороший парень! А вас как зовут?"
    tormod "Чего?.. Тормод меня звать, только это не твоего ума дело, приставай к кому-нибудь ещё"
    me "Ладно... Не подскажите хотя бы, где здесь найти человека, который бы помог оформить документы на вступление в гильдию? Жетоны же так получать нужно?"
    tormod "Ну да, а как ещё? Иди вон в тот угол зала, там писарь, он тебе всё и расскажет. Понаехали тут, тьфу!"
    "Предвкушая, как рыцарь в скором времени начнёт пыхтеть от злости, я поспешно удалился в другую часть корпуса. Видимо, Ред был прав и тут действительно лучше не задавать лишних вопросов"
    "Шагая по мраморному, натёртому до кристалльного блеска по полу, я наткнулся на то маленькое помещение, которое по сути мне и было нужно. Я стоял перед тёмной дубовой дверью с выструганной на скорую руку табличкой: \"Писарь Гильдии\""
    me "Можно войти?"
    "Постучавшись, я приоткрыл дверь, и заглянул внутрь. Кто бы ни был внутри, он явно не очень обрадовался, услышав этот ужасный скрип петель"
    scene bg guild_hall2 with dissolve
    "Писарь: " "Можете заходить, да. Чем могу быть полезен, уважаемый сэр... Как вас зовут? У вас есть жетон с именем?"
    "В комнате, за длинным столом, заваленным письмами и бумаги другого неизвестного мне характера, сидел молодой мужчина с пером и счётами в руках"
    me "Честно говоря, я за этим и пришёл... Мне, и моему другу, нужны жетоны и, как я понял, их можно получить как раз у вас"
    "Писарь на минуту отвлёкся от своих рассчётов и сосредоточил свой пронзающий взгляд на мне и моей старой, грязной сумке, которую я держал за поясом"
    "Писарь: " "Именно так, именно так. Однако, не каждому проходимцу положено иметь жетон, а следовательно, и быть членом городской гильдии. Есть ли у вас какие-либо доказательства, что вы и правда будете полезны королевству?"
    menu:
        "Да, доказательства имеются":
            me "У меня есть доказательства, об этом можете не волноваться"
            "Я вытащил из мешка две грамоты и положил их на стол перед писарем, немного самодовольно улыбаясь. Я чувствовал, что он не ожидал такого от какого-то парня с улицы"
        "Нет, у меня нет доказательств":
            me "Доказательства?.. Это какие же?"
            "Писарь: " "Вы откуда к нам свалились? Грамоты есть? Если есть - давайте, иначе уходите, когда добудете - возвращайтесь. Без них не оформляем, сколько можно повторять!"
            me "Подождите, подождите! Есть грамоты у меня, сейчас достану, только дайте пару секунд!"
            "Я начал быстро рыться в сумке до того момента, пока не извлёк оттуда две потрепавшихся листа бумаги с лентами и печатью. Отряхнув от пыли, я положил их на стол"
    "Писарь: " "Гхм, целых две... Ну что же, ладно, назовите своё имя и имя товарища, которого вы упоминали. Я запрошу гравировку двух медных жетонов, двух грамот хватит только для них"
    me "Меня зовут [me], моего друга - Ред Англаус. Он тоже сейчас в гильдии, если есть необходимость личного присутствия каждого из заявителей"
    "Писарь: " "Далеко не обязательно. В таком случае, оставьте одну грамоту себе, а я запишу вас в учётную книгу как одну группу, чтобы проще было работать с вами"
    "Писарь: " "Ах да, ещё пара вопросов. Вы давно в королевстве? Имеете постоянно место жительство или являетесь членом другой официальной гильдии Инзеля? Отвечайте честно, иначе потом могут возникнуть проблемы"
    me "Членом гильдий не являюсь. Постоянного места жительства пока не имею, ищу как раз, как деньги на него поскрорее заработать. В королевство приехал совсем недавно"
    "Писарь: " "Понятно. Что насчёт вашего друга?"
    me "Он жил раньше в Луфтене, но сейчас, как понимаю, дома своего не имеет. В гильдиях не числится, приехал, как и я, на днях, после месячного отсутствия"
    "Писарь: " "Принято. Я внёс эту информацию о вас, если будет нужно - здесь же сможете получить выписку с печатью. Теперь можете оставить своб подпись в учётной книге"
    "Я взял одну грамоту обратно, а затем расписался в книге за себя и Реда. Через некоторое время писарь отыскал два медных жетона и отдал их мне"
    "Писарь: " "Можете быть свободны... Пока что. Доска объявлений в холле, выполняя задания, всегда показывайте жетон гильдии, чтобы жители знали, откуда вы пришли"
    scene bg guild_hall1 with dissolve
    "Я вышел из тёмной комнаты обратно в главный зал, подкидывая в руке два новеньких зеленоватых жетона с именнованной гравировкой. Пройдя до центра здания, я заметил приближающегося ко мне Реда"
    show Red with moveinright
    red "[me]! Ты где пропадал?! Я тебя уже обыскался, нам же ещё нужно жетоны получить, а ты опять куда-то забрёл и торчишь без дела!"
    me "Ред, ты меня огорчаешь. Я вот уже всё сделал, пока ты там объявления смотрел. Мог бы и не волноваться, это было проще простого"
    "Я протянул Реду его медный жетон, а свой завязал ниткой на шее. Увидев практически окаменевшее недоумевающее лицо Реда, я не мог не рассмеяться"
    me "Пха-х, что ты застыл, вот, бери, он настоящий!"
    red "Быстро ты однако... Я, честно тебе сказать, ещё жетонов не получал, так что не знал даже, как это делается. Но ты видимо на лету схватываешь..."
    me "А то! Ну ты это, тоже, давай показывай, что нашёл из заданий. Не хочется на голодный желудок помирать, да и рука так и чешется пару-тройку монстров завалить"
    red "Мне нравится твой настрой. Давай где-нибудь присядем, я тебе покажу, что нормального смог отыскать. Я не все задания брал, но эти точно будут неплохо оплачены"
    "Мы присели на дубовую скамью и Ред разложил рядом со мной несколько потрёпанных листовок с текстом и красными цифрами, по видимому, ценой награды"
    red "Задание от одного из жителей деревни. Нужно помочь найти пропавшую собаку. Награда: 1 золотая... Что это за бред, опять просят ни пойми что. Ладно, пошли дальше..."
    red "задание от городского банка. Помогите найти преступника, укравшего драгоценности из казны. Очень миленько, дают несколько золотых"
    red "И последнее - доставить товар до порта Луфтена с окраины города. Все условия при встрече, оплата не менее двух золотых. Хм, последнее неплохо выглядит"
    me "Ух, как интересно! Мне уже не терпиться отправиться в путешествие по одному из квестов, только представь, скоро нам не придётся перебираться с злеба на воду!"
    red "Ну да, конечно, так всё мигом и случится"
    "Ред собрал обратно все бумаги и убрал их в свою сумку. Затем встал, и направился к выходу, позвав меня с собой"
    scene bg luften_square with fade
    show Red at center
    me "Эй, Ред, я так не понял, мы будем выполнять эти задания или бросим эту затею до лучших времён?"
    red "Конечно будем, куда нам деваться. Денег почти нет, а все эти квесты обещают какую-никакую награду... Кроме купца, но там разберёмся"
    red "Просто это всякие мелкие делишки, которые нас обеспечат ну максимум на пару дней. Ещё учитывая, что нужно закупать снаряжение, зелья, точить тебе клинок..."
    red "В общем, нужно скорее заработать грамот и получить повышение. Чем выше ранг, тем больше шанс, что сможем получить задания подороже. Приплюсуй ещё, что твой опыт к тому моменту умножиться не в один раз"
    "Да, Ред вроде говорил, что за несколько грамот дают повышение, а с определённого момента начинают выплачивать деньги. Видимо, он этого и добивается, хитро"
    me "Да... Наверное ты прав, впрочем, ты в этом деле и должен лучше меня разбираться"
    "Мы прошли обратно по площади, уже заметно опустевшей после полуденной давки. Рыцаря того уже не было, да и народ успокоился и мирно шёл по своим делам. Странный однако это город, Луфтен!"
    jump luften_explore

label luften_quests1:
    if expl_choice1 and expl_choice2:
        $ expl_choice1 = False
        $ expl_choice2 = False
        jump luften_night
    else:
        menu:
            "Проверить таверну Иоганна" if not expl_choice1:
                $ expl_choice1 = True
                jump Iogann_tavern
            "Найти преступника" if not expl_choice2:
                $ expl_choice2 = True
                jump luften_burglar

label Iogann_tavern:
    $ stage = "Северный район Луфтена"
    $ chapter = 4
    $ save_name = "Глава " + str(chapter) + ". " + stage

    if box_given:
        me "Я думаю, уже пора проверить, получил ли свою посылку Иоганну, времени прошло достаточно"
    else:
        me "Думаю, теперь стоит отнесьти посылку Иоганну, времени прошло достаточно"
    show Red with moveinright
    "Твоё право. Надеюсь, там дадут приличную награду, а то лишний раз подниматься в гору не особо хочется"
    scene bg luften2 with dissolve
    "Ред и я снова направились в северный район Луфтена, в таверну, некогда около которой мне пришлось убить трёх бандитов"
    "Интересно, вроде как время прошло, а ловить меня никто не стал. Неужели действительно в Луфтене можно действовать настолько безнаказанно?"
    "Эта Инквизиция... По договору они должны следить за порядком, но на деле они не лучше стражи, есть подумать"
    "Я размышлял о моих прошлых поступках, пока поднимался в гору. Странно, но я не сожалел. И от этого становилось ещё противнее на душе"
    scene bg luften3 with dissolve
    "Поднявшись на самый верх, я почуял, что что-то изменилось на улице с тех пор, как мы были здесь. Тут стало как-то тише, никаких признаков жизни"
    "Вся улица словно опустела, даже дым не шёл из домов, а окна все были захлопнуты, словно нарочно"
    me "Ред, у меня нехорошее предчувствие..."
    red "У меня тоже. На улицах ни души. Держи меч наготове, на всякий случай"
    "Я следую совету Реда и иду по улице к тому месту, где располагалась таверна, попутно оглядываясь по сторонам"
    "Ред медленным шагом следовал за мной, всё было абсолютно тихо. Тихо, пока мы не дошли до поворота к таверне"
    "Приближаясь к зданию, я всё же начал слышать какие-то голоса за углом, а также лязг металла об каменную мостовую"
    me "Скорее всего там несколько человек, причём в доспехах. Неужто, ещё одна банда разбойников?"
    "Что бы это ни было, нужно действовать! Я вытаскиваю меч из ножен, и собираюсь выпрыгнуть на противника, как вдруг..."
    show guardian_left at left with fade
    show guardian_right at right
    "Стражники: " "Не двигаться! Положите оружие на землю и медленно поднимите руки над головой!"
    "Будто из под земли передо мной выросли два огромных воина в золотых доспехах, в плащах и с секирами в руках. От такого неожиданного поворота событий я чуть было не выронил меч"
    "Это Луфтенская стража?.. Откуда она здесь взялась, и почему именно сейчас? Видимо, сейчас на эти вопросы мне вряд ли ответят, так что..."
    menu:
        "Добровольно сдаться":
            "Я медленно кладу меч на землю и подымаю свои руки вверх. Ред следует за мной, молча глядя то мне в затылок, то на двух высоченных стражников"
            "Стражники: " "Именем короля Эрлиха II, вы двое арестованы и предстанете перед законом в соответствии..."
            "Не успел стражник договорить свою карательную речь, как новая фигура возникла перед нашими глазами. Кто бы мог поверить, что это был..."
        "Вступить в бой с рыцарями":
            me "Ну уж нет, я так просто не сдамся, тем более, ни за что! Думаете, вы сильнее всех, раз имеете в руках оружие побольше?!"
            "Я достаю свой меч, не смотря на то, что передо мной стоят двоё самых настоящих воина. Проходит доля секунды, и они уже готовы нанести удар..."
            "Только счастливая случайность спасла меня в этот момент. Стоя на волоске от смерти, я слышу чей-то суровый, властный голос за спиной. Кто бы мог поверить, что это был..."
    show Shtrauf with fade
    shtrauf "Отставить рядовой. У вас нет оснований для ареста этих двух граждан. Вы оба, уберите своё оружие!"
    "Человек в сверкающей чёрной стальной броне вышел из-за спин стражников. Яркий развевающийся плащ, огненный меч на поясе, суровый, словно гром голос - вне сомнения, это был сэр Штрауф"
    "Подчиняясь приказу, я и стражник опускаем своё оружие. Ред, отряхиваясь, выходит из-за моей спины на обозрение главнокомандующему"
    red "Сэр Штрауф, большая честь увидеть вас здесь, если бы я знал, что сам член бриллиантовой гильдии выйдет в городской район Луфтена..."
    shtrauf "Долой разговоры без разрешения! То, что я отдал приказ страже не трогать вас, ещё не говорит о том, что вы можете уйти отсюда. У меня к вам есть несколько вопросов"
    hide guardian_left with dissolve
    hide guardian_right with dissolve
    "Сэр Штрауф кивнул своим рыцарям, и те поспешно удалились за поворот, оставив нас троих наедине на пустынной мостовой"
    shtrauf "Для начала скажите ваши имена, а лучше покажите, есть ли у вас документы членов гильдии. Это сильно упростит наш с вами разговор"
    red "Ред Англауз. Его зовут [me], фамилии нет. Можете проверить"
    "Я вынул из сумки документы и протянул их в протянутую руку Штрауфа. Резкими движениями своих стальных перчаток он осмотрел бумаги на предмет подлинности"
    shtrauf "Понятно. В таком случае, перейдём непосредственно к вопросам. Вопрос первый: зачем вы пришли в этот район и были ли здесь раньше"
    "Я бросил взгляд на Реда, но тот стоял не двигаясь и, по-видимому, не собирался отвечать на вопросы рыцаря, предоставив эту задачу мне"
    $ choice = 1
    menu:
        "Мы шли в тавену Иоганна":
            $ choice = 1
            me "Мы шли в таверну Иоганна по одному личному делу. Я был здесь до этого, пару дней назад, по тому же поводу, мне нужно было отдать посылку"
        "Мы оказались здесь случайно, впервые":
            $ choice = 0
            me "Мы оказались здесь случайно, мы всего лишь путешественники, искали где бы поесть. Раньше здесь никогда не были"
        "Промолчать":
            "Я тоже решил не отвечать на вопросы. Кто знает, может он уже всё знает, или наоборот... Лучше не подавать виду, что мне что-либо известно"
            "Сэр Штрауф прождал секунд десять, а затем достал из-за пазухи свой сверкающий меч. Ударив ботинком по каменной мостовой, он произнёс: "
            shtrauf "Молчание не принимается. Если вы не будете отвечать на мои вопросы, не думайте, что сможете уйти отсюда живыми"
            menu:
                "Мы шли в тавену Иоганна":
                    $ choice = 1
                    me "Мы шли в таверну Иоганна по одному личному делу. Я был здесь до этого, пару дней назад, по тому же поводу"
                "Мы оказались здесь случайно, впервые":
                    $ choice = 0
                    me "Мы оказались здесь случайно, мы всего лишь путешественники, искали где бы поесть. Раньше здесь никогда не были"
    "Если бы я видел его лицо за этой устрашающей чёрной маске... Не могу понять, правильно ли я поступаю, вдруг, это обернётся для меня чем-то похуже простого допроса?"
    shtrauf "Ваш ответ понятен. Хорошо, в таком случае следующий вопрос: знакомы ли вы с хозяином местной таверны, Иоганном, разговаривали ли с ним лично?"
    if choice == 0:
        "Видимо, придётся и дальще гнуть палку. Эх, ладно, будь, что будет"
        me "Понятия не имею, о ком вы. Мы не знакомы ни с каким Иоганном, к тому же и в местных тавернах никогда не были"
        "Штрауф на секунду замер, но вовремя вернулся к своей непринуждённой позе. по-видимому, допрос уже подходил к концу"
        shtrauf "И о нескольких смертях близ этой таверны вы понятия не имеете, так?"
        "Эти слова, сновно молнии, прошлись по моему телу. Неужели, он всё-таки что-то знает... Нет, ведь не мог же он всё это время играть со мной..."
        menu:
            "Я слышал об убийствах":
                me "Кое-что слышал... убиты несколько человек, я прав?"
                "Из под шлема раздался небольшой смешок. Одно мгновение, и меч Штрауфа уже касался моей шеи"
                shtrauf "Вы правы. Однако данная информация является строго засекреченной и не распространяется. Раз вы не местные, боюсь, вы непосредственно связаны с этим преступлением"
                shtrauf "В таком случае, мне не остаётся иного выбора. Я вынужден вас арестовать, а в последствии отправить в суд, где вам вынесут приговор"
            "Не имею понятия о чём вы":
                me "Нет, не слышал, само собой. К нам это не имеет никакого отношения"
                shtrauf "Вот как... Очень интересно, очень интересно. А что скажете насчёт десятка свидетелей вашей драки у таверны?"
                "Свидетелей? Нет... Пропади всё пропадом! Он знал всё с самого начала и просто играл со мной! Зачем, зачем я пытался обмануть?.."
                me "Драки близ таверны... Д-да, наверное, было такое..."
                shtrauf "Ага. Господин [me], господин Ред. Вынужден вас арестовать, вы подозреваетесь в убийстве нескольких человек, а также в сокрытии факта преступления. Сдайте всё своё оружие и подымите руки вверх"
        me "За убийство этих отбросов общества?! Трёх негодяев, покушающихся на жизнь ни в чём неповинных граждан?! А как бы вы поступили на моём месте?!"
    else:
        me "Нет, мы не были знакомы с ним лично, однако собирались. Как я сказал раньше, у нас было к нему дело"
        shtrauf "А что вы скажете насчёт нескольких смертей близ таверны? Тоже об этом знаете?"
        menu:
            "Да. Это сделал я":
                me "Прекрасно знаю. Это я убил тех троих разбойников, покушавшихся на жизни ни в чём неповинных граждан. Я ни капли не жалею о своём преступлении, так что не вижу смысла что-либо таить"
            "Нет, об этом не слышал":
                me "Нет, не слышал, само собой. К нам это не имеет никакого отношения"
                shtrauf "Вот как... Очень интересно, очень интересно. А что скажете насчёт десятка свидетелей вашей драки у таверны?"
                "Свидетелей? Нет... Пропади всё пропадом! Он знал всё с самого начала и просто играл со мной! Зачем, зачем я пытался обмануть?.."
                me "Драки близ таверны... Д-да, наверное, было такое..."
                shtrauf "Ага. Господин [me], господин Ред. Вынужден вас арестовать, вы подозреваетесь в убийстве нескольких человек, а также в сокрытии факта преступления. Сдайте всё своё оружие и подымите руки вверх"
                me "За убийство этих отбросов общества?! Трёх негодяев, покушающихся на жизнь ни в чём неповинных граждан?! А как бы вы поступили на моём месте?!"
    "Повисло молчание. Сэр Штрауф посмотрел на меня, потом на Реда, потом снова на меня. Такое ощущение, будто я произнёс что-то невероятное"
    shtrauf "Разбойников? Вы о ком это говорите? Произошло двойное убийство бармена и хозяина таверны, не несите, пожалуйста, этот бред"
    me "В смысле хозяина и бармена?.. Вы же говорили о..."
    shtrauf "Я говорил именно о них. Тех троих уже давно забрала инквизиция и сожгла, никому дела до них не было. То есть вы хотите сказать, что не слышали об этом?"
    if box_given:
        me "Нет конечно! Я отдал посылку бармену, а сегодня хотел поговорить с хозяином насчёт награды за неё. Неужели, в ней дело?"
    else:
        me "Нет конечно! Я хотел отдать посылку хозяину и получить награду за неё. Неужели, в ней дело?"
    shtrauf "Не знаю. Где она сейчас? Когда точно вы встречались с барменом в таверне?"
    me "Говорю, пару дней назад. Там я и подрался с разбойниками, которые хотели отнять её. После этого я занимался обычными делами в городе, я думал, всё нормально..."
    "Повисло нервное молчание. Штрауф нервно ударил ногой по каменной брусчатке"
    if box_given:
        shtrauf "Нужно пройти в таверну и узнать, лежит ли она там. Стража! Осмотреть здание вдоль и поперёк!"
    else:
        shtrauf "Она же сейчас у вас? Доставайте скорее, если вы её не вкрывали раньше, то сейчас самое время!"
    scene bg black with fade
    "Внезапно раздаётся колоссальный взрыв, и всю улицы наполняет чёрный дым. Ударной волной нас всех отбрасывает на тротуар"
    me "Что за чёрт... Эй, Ред, Штрауф, вы меня слышите?!"
    "Я привстаю с земли и осматриваюсь по сторонам. Кругом меня непроглядный дым, где-то вдалеке слышны крики стражи и горожан"
    "Резкая боль близ живота прошла по всему телу. Приложив руку к своему боку, я почувствовал, как оттуда течёт кровь"
    me "Гхе-гх... Ред!"
    shtrauf "Заклинание первого ранга! Грозовой ветер!"
    "Я слышу голос Штрауфа позади меня. Не успел я отойти в сторону, как чудовищный поток воздуха смывает меня обратно на камень. Чёрный дым начинает рассеиваться"
    scene bg Vaal_first with fade
    "В нескольких метрах от меня возвышается ужасающая чёрная фигура с огромным двуручным мечом. Колоссальное зло исходило от этого человека, если Это можно было им назвать"
    "Одна рука его полыхала синим пламенем, которое, видимо и вызвало тот чудовищный взрыв. Другая постукивала трёхметровым мечом по камням тротуара"
    "Даже стоя перед ним, сложно было понять, есть ли что-то человеческое в этом существе. Он был больше похож на чистое зло, нежели на простого воина"
    "Вдруг ужасающие звуки раздались из под маски создания. Трудноразличимые, низкие, но чрезвычайно громкие - это были слова, слова произнесённые этим монстром"
    vaal "Думаю стоит представиться, меня зовут Ваал, я один из четвёрки Вестников Тьмы"
    vaal "Впрочем, не думаю, что наше знакомство продлится долго. Не люблю болтать попусту"
    vaal "Отдайте её. Не вижу смысла обрекать себя на вечные муки, в ваших же интересах подчиниться мне"
    "Её? Неужели он говорит о шкатулке?.."
    if not box_given:
        "Я медленно протягиваюсь в сторону своей сумки, но замечаю, что её уже нет за моей спиной"
    show shtrauf at right with fade
    shtrauf "Не думай, что имеешь право командовать в этом городе, кем бы ты ни был. Убирайся, пока не получил по заслугам!"
    "Рядом со мной встаёт сэр Штрауф, обнажая пламенный меч. В руках он держит ту самую шкатулку, каким-то образом подобранную им во время задымления"
    shtrauf "Вы оба, бегите, я задержу его на сколько смогу"
    "Я делаю последние усилия, чтобы встать и помогаю Реду отойти за ближайший угол дома. Истекая кровью, я что есть силы пытаюсь отойти как можно дальше от поля предстоящей битвы"
    shtrauf "Заклинание третьего ранга! Пламенное кольцо!"
    "Штрауф выкрикивает заклинание и огромное огненное кольцо окутывает район города, изолируя его и Ваала от остального мира. Начинается воистину свирепый и невиданный ранее бой"
    scene bg Vaal_second with dissolve
    vaal "Как наивно предполагать, что нечто подобное меня остановит. Может быть не сегодня, но своей цели я достигну"
    shtrauf "Хм, ещё увидим. Ну что же, можешь нападать, а то по виду только трепаться и умеешь"
    $ renpy.block_rollback()

    define Vaal_vs_Shtrauf = None

    $ attacks = []
    $ attacks.append(attack("Ваал атакует гиганстским мечом!", std_base_attack, 60000, 0)) #base
    $ attacks.append(attack("Ваал использует шар ледяного огня!", std_base_attack, 40000, 0)) #base
    $ attacks.append(attack("Ваал использует силу тёмной энергии!", std_base_attack, 50000, 0)) #base
    $ attacks.append(attack("Ваал заряжает энергией свой меч, уничтожая всё вокруг!", std_block_attack, 10000, 0)) #block
    $ attacks.append(attack("Ваал использует приём: Великий Удар Тьмы!", std_base_attack, 120000, 0)) #after-block
    $ attacks.append(attack("Ваал создаёт тёмный барьер!", std_wait1_attack, 2500, 0)) #wait
    $ attacks.append(attack("Ваал обрушивает огромную волну тьмы!", std_wait2_attack, 1000000, 0)) #after-wait
    $ attacks.append(attack("Ваал создаёт непроницаемый барьер вокруг своего тела!", max_heal_skill, 0, 0)) #heal

    $ Vaal_vs_Shtrauf = enemy("Ваал, Вестник Тьмы", 500000, std_enemy_update, std_enemy_rand)
    $ Vaal_vs_Shtrauf.attacks = attacks

    $ Player = player(249, 0, std_player_update)
    $ Player.max_health = Player.health = 100000
    $ Player.attacks.append(attack("Пламенный Клинок", sample_attack, value = 20000, cost = 10))
    $ Player.attacks.append(attack("Огненная Буря", sample_attack, value = 40000, cost = 20))
    $ Player.attacks.append(attack("Первородный Огонь", sample_attack, value = 60000, cost = 30))
    $ Player.attacks.append(attack("Разрушитель Небес", heaven_destroyer, value = 100000, cost = 50))

    $ Log = log(std_win_check, std_lose_check, std_log_update, "Битва между Ваалом и Штрауфом началась!")

    call screen fight_screen(Log, Player, Vaal_vs_Shtrauf)

    $ renpy.block_rollback()

    scene bg Vaal_first with fade

    vaal "Как ты... Как ты посмел противостоять мне, самому..."
    "Ваал упал на колени, истощённый и израненный атаками Штрауфа. Не в силах более продолжать бой, он убрал свой меч за спину"
    vaal "На этот раз победа в действительности за тобой, Штрауф"
    vaal "Однако, я более не пропущу промаха. Ради своего господина, ради его желания, я одержу верх и над тобой"
    vaal "Заклинание четвёртого ранга: мгновенная телепортация!"
    scene bg luften3 with fade
    "Воин испарился в одно мгновение, не дав Штрауфу нанести смертельный удар. Пламя кольца рассеялось, оставив после себя обушленные дома и улицы"
    "Не менее изуродаванный многочисленными порезами, сэр Штрауф упал на обугленную землю, уронив меч рядом с собой. Он был на волоске от своей гибели"
    shtrauf "Да, не повезло мне... Город спасён, только вот... Самому бы в живых после такого остаться"
    me "Господин Штрауф, вы в порядке?"
    "Я подбегаю к лежавшему на земле рыцарю и помогаю ему подняться с тротуара. По моей руке стекает кровь генерала"
    shtrauf "Гхх... Я в порядке, просто немного... устал, гхе-х"
    show Red at center with dissolve
    red "Дай ему лекарственное зелье, скорее! Не видишь, что он кровью истекает!"
    "Подбежавший Ред протягивает мне пузырёк лекарственной смеси и я даю его Штрауфу. В то же время к нам подбегает городская стража"
    show guardian_left at left with moveinleft
    show guardian_right at right with moveinright
    "Стражники явно выглядели шокированными. Огородив улицу от посторонних глаз, они встали рядом со мной и генералом, наблюдая за тем, как я перебинтовываю раны воина"
    hide Red with dissolve
    show Shtrauf at center with dissolve
    shtrauf "Да уж, ну и сильно я влип... Если честно, я уж решил, что жизнь моя к концу подходит. Чтобы я без вас делал!"
    me "Что вы, сэр Штрауф, это мой долг - помогать таким людям, как вы... А где Ваал? Он мёртв?"
    shtrauf "Мгх, боюсь, что нет. Шкатулка по прежнему у меня, что бы в ней не лежало. Но этот монстр смог сбежать, простите"
    shtrauf "Я нанёс ему достаточно ранений, чтобы он не сунулся в город в ближайшее время. Но нужно быть готовым и к повторной атаке"
    shtrauf "Так что же внутри вашей шкатулки? От неё есть ключ?"
    me "Нет, к сожалению... Я думал, что владелец обладает им, да и вообще просто хотел получить немного денег с доставки. Кто бы мог подумать, что всё так обернётся..."
    shtrauf "Никто само собой. Однако, если вы не возражаете, теперь она будет храниться у меня. Раз за ней ведётся такая охота, то там явно что-то ценное"
    me "Да, конечно. Ещё раз спасибо вам, сэр Штрауф. Без вас городу пришёл бы конец"
    shtrauf "Это моя работа парень. Ну что же, думаю, мы можем расходится. Если что узнаете - приходите в городскую гильдию и требуйте встречи со мной. Я буду там"
    "Штрауф подобрал с тротуара свой меч и отряхнул плащ от пыли и пепла. Стражники выстроились в ряд, ожидая дальнейших указаний. Главнокомандующий встал перед ними, и напоследок бросил на нас свой взгляд"
    shtrauf "Кстати, вы же вроде как путешественники. Я наверное должен дать хоть небольшую награду за старание. Думаю, этого будет достаточно, не обижайтесь, больше с собой попросту нет"
    "Штрауф достал из под плаща мешочек со звенящими монетами и отдал его Реду в руки. Затем, похлопав меня по плечу своей огромной рукой, отдал нам честь"
    shtrauf "[me], Ред, удачи вам. Надеюсь ещё встретимся, быть может даже в более мирной обстановке. Прощайте"
    scene bg luften3 with dissolve
    "Воин развернулся и направился в сторону королевского дворца. Под лязг доспехов Луфтенская гвардия проследовала за ним"
    show Red at center
    red "Ну и денёк... Посылку мы не отдали, чуть было не погибли, повстречали генерала Луфтенской армии... Что же тебя так тянет в такие передряги?"
    me "Видимо судьба, Ред, не иначе. Я бы и сам хотел знать, как я это умудряюсь делать... Но задание же можно считать выполненным! Деньги-то у нас есть!"
    red "И то верно. Ну-ка, сколько тут нам подарил наш дорогой Штрауф... 1, 2, 3... 6! Шесть золотых! Ну, приятель, теперь заживём! Этого нам надолго хватить должно"
    "Так, стоя на покрытой пеплом улице, мы радовались полученной награде. Хоть в этой битве мы и не принимали непосредственное участие, но деньгиы заслужили сполна"
    hide Red with dissolve
    "Я и Ред прошли по обгоревшей улице назад к лестнице. Постепенно люди начали выходить из своих домов, поняв, что всё наконец закончилось"
    "Удивительно, но многие были даже не удивлены произошедшим, будто это в порядке вещей. Неужели здешний народ так сильно привык к таким потрясениям?"
    "Так или иначе, нам с Редом предстояло ещё немало дел, и останавливаться на достигнутом было нельзя. Какое же будет наше следующее задание?"
    jump luften_quests1

label luften_burglar:
    $ stage = "Восточный район Луфтена"
    $ chapter = 4
    $ save_name = "Глава " + str(chapter) + ". " + stage
    me "Предлагаю найти того разыскиваемого преступника с объявления, за него полагается неплохая награда"
    show Red at center with dissolve
    red "Хм, тут я согласен, лишних золотых не бывает. Только вот, как ты собрался его искать?"
    me "В объявлении сказано, что он ограбил несколько банков. Думаю,  с них и начнём. Расспросим, что, да как"
    "Ред удовлетворительно кивнул мне в ответ и мы вместе направились в сторону ближайшего Луфтенского банка, стоявшего по словам старика в восточном районе города"
    scene bg luften4 with dissolve
    "Пройдя некоторое время по мостовой, мы оказались за пределами центра Луфтена. Казалось бы, меня уже было ничем не удивить, но вот снова невообразимые пейзажи открылись моему взору"
    "Дома в этом районе по большей части не были жилыми, а прохладный бриз, то и дело обдувавший меня, не давал забыть о том, что буквально в паре километров отсюда располагается порт"
    "Пока мы шли по постепенно темнеющей улице, я вспомнил свой недавний разговор с Йозефом. Один вопрос по прежнему не давал мне покоя, и не смотря на совет графа об этом не спрашивать, я обратился к Реду"
    me "Ред, слушай, помнишь по пути в Луфтен ты рассказывал историю о битве с Пламенным Драконом?"
    "Ред чуть сбавил шаг и посмотрел в мою сторону, словно я опять сказал нечто глупое"
    red "Ну помню, не так давно это было. А что, я вроде всё и так рассказал, если уснул в тот момент, то уж прости, пересказывать не буду"
    me "Да нет! Я не об этом. Я просто хотел вот о чём спросить: ты вскольз упомянул в своём рассказе рыцаря Цвайна, ещё сказал, что он каким-то артефактом обладает... Или типо того"
    me "Не мог бы поподробнее о нём рассказать? Мне как-то стало интересно, когда мы были в гостях у Йозефа, а он на такой вопрос отвечать отказался"
    red "Мда... Вот ты о чём хотел спросить. Видимо, я лишнего тогда наговорил, но ладно, слово не воробей, так уж и быть, расставлю все точки на i"
    scene bg Cvain with fade
    red "Цвайн - один из лучших мечников и магов Инзеля, а также бывший владелец бриллиантового ранга гильдии Мариэна, к тому же и воин, убивший Пламенного Дракона двадцать лет назад"
    red "К сожалению, немногим позднее этот человек был приговорен трибуналом к смертной казни за использование некромантии на людях, запрещённого в Инзеле исскустве"
    red "Само собой, он не мог так просто погибнуть, и вскоре после вынесения приговора бежал из королевства на нейтральные земли и пропал из виду вплоть до наших дней"
    red "Было послано несколько отрядов, но мало кто вообще вернулся живым. Так как нейтральные земли всегда были полем боя сразу нескольких больших группировок, искать в них конкретного человека почти бессмысленно"
    red "Ситуацию осложнило и то, что Цвайн унёс с собой и таинственный артефакт, по сути принадлежавший императору Мариэна, Вингерму"
    red "В конечном итоге мечник просто был признан изменником во всех трёх королевствах, данные об убитых солдатах стёрли, и это дело замяли"
    red "Хоть до сих пор и ходят слухи о том, что этот человек появляется в столицах королевств, но официально его пока никто не обнаружил, поэтому населению было велено не поднимать паники зазря и вообще его не упоминать"
    scene bg luften4 with dissolve
    red "К слову, на данный момент известно сразу несколько гипотез о том, что же всё-таки стало с Цвайном. Одни говорят, что он умер в бою с одной из группировок Инзеля, во что я слабо верю"
    red "Другие - что он засел где-то в горах и готовит свою армию для восстания и захвата материка, что уже вполне возможно, учитывая его потенциал"
    red "Ну и третьи считают, что Цвайн сговорился с Имером IV, императором Фандера и сейчас находится у него во дворце в качестве телохранителя. Так как само королевство почти закрытое, то в это тоже можно поверить"
    red "Что до тебя, то я советую тебе действительно не лезть в это и не придерживаться никакой из этих точек зрения. Пока это тебя не касается, и я надеюсь никогда и не каснётся"
    me "Понятно. Ты, правда, как обычно вызвал своим рассказом у меня только больше вопросов, Ред. Но, видимо, в другой раз. Мы ведь уже почти пришли?"
    red "Вроде как, если память не подводить, прямо за этим углом будет вход на восточную площадь... Да, то самое место!"
    scene bg luften5 with dissolve
    "Мы вышли к небольшому скверу перед большим мраморным зданием с развивающимися флагами Луфтена, переливающемся в лучах заходящего солнца"
    "На красивом ухоженном газоне слева стояла большая статуя молодового Императора Эрлиха II, с другой стороны журчал красивый чистый фонтан, словно выстроенный совсем уж недавно"
    "Пройдя ближе к входу в здание, я заметил, что здесь всё же тут всё не так безоблачно, как казалось на первый взгяд: у ворот стояло сразу несколько стражников, а вместе с ними и один купец, что-то яростно доказывая им"
    show guardian_right at right with moveinright
    show banker at left with moveinleft
    banker "Да! Он был здесь прошлой ночью, говорю вам, тупоголовые! Вы вообще работаете или только херней страдаете?!"
    me "Извините, сэр, вы обсуждаете тот заказ, который оставили в гильдии? Мы пришли сюда как раз по нему, готовы помочь"
    banker "Что?.. А, да, именно по этому поводу. Вы путешественники? Я уж совсем отчаялся, начал с этими дубоголовыми отношения выяснять. Идите прочь"
    hide guardian_right with moveinright
    show banker at center with moveinleft
    "Стражник буркнул что-то себе поднос и отошел в сторону, звеня своими блестящими доспехами. Казалось, будто он в действительности не желал ничего делать, а просто шатался по скверу без дела"
    me "Позвольте представиться, моё имя - [me], это мой товарищ - Ред. Пришли, чтобы разузнать про задание о преступнике, в частности выполнить"
    banker "Очень, очень хорошо! Готов ответить на любые вопросы, буду очень признателен, если поможете. Награда будет в точности по договору"

label banker_questions:
    if not (ask_counter1 and ask_counter2 and ask_counter3 and ask_counter4):
        hide banker
        menu:
            "Что конкретно произошло?":
                show banker
                me "Расскажите поподробней, что же произошло этой ночью, всё, что помните"
                banker "Да собственно, меня и не было в банке, когда это произошло. Кто-то вломился внутрь, украл всё содержимое хранилища и скрылся. Пропажу заметили лишь утром"
                banker "Главное - все стёкла в здании и дверях были целы. Не могу понять, как ему удалось оказаться внутри. Стража тоже была на месте, и они опять же никого не заметили"
                banker "Одним словом, бред какой-то, понятия не имею, что теперь делать, даже где искать вора"
                $ ask_counter1 = True
                jump banker_questions
            "Что украл преступник?":
                show banker
                me "Скажите, что было украдено из банка. Это были драгоценности или может какие-то ассигнации?"
                banker "Почти всё были обычные деньги, хранившиеся в мешках и сундуках. На самом деле внутри было не так много, поэтому человек вполне мог справиться с этим в одиночку"
                banker "Это были деньги клиентов, хранившиеся на сберегательных счетах. Поэтому очень важно, чтобы вы смогли найти всё как можно скорее"
                me "Да-да, конечно, мы постараемся..."
                $ ask_counter2 = True
                jump banker_questions
            "Кем вы конкретно являетесь?":
                show banker
                me "К слову, не могли бы вы сами представиться. Очень хотелось бы знать, с кем имеешь дело"
                banker "Да, конечно. Я банкир, управляющий счетами клиентов банка и распределяющий доходы. Не скажу, что являюсь главным в этом учреждении, но должность весьма значимая"
                me "Вы непосредственно оставляли заявление в гильдии?"
                banker "Да, так как эта проблема к сожалению лежит на моих плечах. Я решил, что быстрее будет отдать всё в руки таких как вы, чем ждать, пока разберуться власти или ещё кто похуже"
                $ ask_counter3 = True
                jump banker_questions
            "Есть ли у вас какие-то улики?":
                show banker
                me "У вас нет улик или зацепок? Что угодно, что могло бы помочь нам и ускорить ход дела. Может быть, нам всё же стоит распросить стражу?"
                banker "Можете, но, как видите, они мало что знают. Зацепок очень мало, считайте что их вовсе нет. Вор не оставил отпечатков, только какие-то грязые пятна на полу были, может быть следы"
                me "Следы? То есть вы знаете, куда он ушёл? Хотя бы направление?"
                banker "Да говорю же, нет ничего! Просто пятна на полу в хранилище, за пределами ничего нет. К слову, решётка комнаты осталось нетронутой, как и дверь внутрь"
                $ ask_counter4 = True
                jump banker_questions
    $ ask_counter1 = False
    $ ask_counter2 = False
    $ ask_counter3 = False
    $ ask_counter4 = False
    me "Да уж, очень и очень странно. То вы есть хотите сказать, что преступник, не разбивая окон, ни ломая дверей и решётки, пробрался внутрь, оставив следы только внутри, украл всё и скрылся?"
    banker "Получается, что всё так. Стража конечно может быть причастна, но вероятность мала, сейчас такое время, что за любое преступление можно лишиться головы или ещё похоже... бррр!"
    me "Может тогда стоит осмотреть конкретно то хранилище? Раз других зацепок нет, то найти что-то можно только там"
    banker "Гхм... Ладно, туда правда просили никого не пускать так как это место преступления, но вам думаю всё-таки можно. Идите за мной, я проведу вас внутрь"
    "Мы с Редом прошли за банкиров внутрь мраморного здания. Не особо задерживаясь на верхних этажах, путеводитель сразу повёл нас вниз по винтовой лестнице, где по его словам и находилось хранилище"
    scene bg vault with fade
    "Мы оказались в подземном помещении, более похожем на темницу, нежели банковское хранилище. Здесь, в тёмном и пустом месте как никогда чувствовалась опасность, будто подстерегавшая меня за ближайшим углом"
    show banker at left with dissolve
    show Red at center with dissolve
    banker "не пугайтесь здешних помещений, знаю, они выглядят ужасно и больше смахивают на место пребывание заключенных, но здесь действительно храняться деньги банковских клиентов"
    red "Чем же обусловлен такой дизайн интерьера? Неужели Луфтенский банк не придумал ничего покрасивее темницы для хранения денег?"
    banker "Всему виной история этого места. Ведь банки в Луфтене существуют относительно недавно, может лет пятьдесят. Раньше на этом месте располагалась тюрьма, но с развитием города её перенесли на остров Туас, думаю слышали"
    banker "Хоть наземное здание и было снесено ввиду его уродливости и старины, подземелье было решено оставить и утилизовать как склады и хранилища. Их строили на века, так что шанс обвалов или затоплений минимален"
    banker "К слову, для дождевых вод, которые в любом случае будут попадать сюда, предусмотрен проточный канал, ведущий прямо в сторону моря, по коротому вода утекает. Когда-то это был первый прототип канализации!"
    red "Спасибо за краткий эксурс в историю этого места. Однако, мы всё ещё ничего не узнали, лучше покажите, где находится та комната, в которую пробрался грабитель"
    banker "Да, одну секундочку, нам с вами прямо по коридору, а затем направо. Там как раз секция сберегательных счетов"
    hide Red
    hide banker with fade
    "Банкир повёл нас по коридору вглубь подземелья, захватив с собой один из стоявших у входа факелов. Освещая им путь, мы шли по мрачному коридору, вдоль потертых, увешанных паутиной стен"
    banker "Да, это где-то здесь, в этой комнате... Да, вор был тут, а замок нетронутый, даже пыль сохранилась. Ну что же, можете осматриваться. Только недолго, пока стражи здесь нет"
    "Я остановился перед дверью и начал осматривать окружающее помещенье. Ред же вместе с банкиром аккуратно приоткрыли дверь хранилища и зашли внутрь"
    show Red at center with dissolve
    red "Пятна на полу действительно есть, и их много, когда как за пределами подземелье относительно сухое. Много следов, но все они сконцентрированы в одном месте где-то по центру комнаты"
    me "У меня тут действительно ничего нет. Ни следов, ни каких-либо повреждений стен... Эй, а что это журчит в отдалении?"
    show banker at left with dissolve
    banker "Журчит? А, водосток, о котором я говорил. Его переодически используют и для слива отходов, так что не удивляйтесь, такое тут постоянно"
    me "Вы хотите сказать, что он проходит прямо за этой стеной?"
    banker "Ну точнее под нашими ногами, но да, он тесно связан с здешними коридорами, смывая дождевую воду и..."
    "Банкир замялся и кажется тоже кое-что понял. Ред также застыл и прислушался к плеску воды, доносившемуся из под каменного пола хранилища"
    red "Ну и дела! А ну, шаг в сторону, посмотрим, насколько хорошо защищено ваше хранилище!"
    "Ред оттолкнул банкира и ударил что есть силы ногой прямо по центру комнаты, где и было больше всего грязых луж. Пол хрустнул, и всё подземелье огласил гул стекающей по каналу воды"
    red "Эгей, да это джекпот! Прямо под нами... Нет, под нашим носом находится чёрный ход в банк. И как же раньше вы не смогли заметить такую брешь, а?"
    hide banker with moveinleft
    "Банкир покраснел и отошёл в угол комнаты, бормоча ругательства себе под нос. Я же подошёл к Реду и заглянул в образованную в полу дыру"
    me "Это городская канализация, по ней грабителю не составило труда залезть внутрь и украсть всё. Достаточно обычной бочки, чтобы справить по течению весь товар прямо к портовому стоку"
    red "Думаю, нам стоит спуститься вниз и узнаить всё собственнолично. Как никак, наша работа, лезть во все щели и дыры, не находишь?"
    "Ред улыбнулся и аккуратно спрыгнул вниз в канализационный тоннель. Я, сказав банкиру ждать нас в течение этого дня в сквере, также скрылся из виду в глубинах Луфтена"
    scene bg sewage1 with fade
    "Вступив на склизкий мокрый пол, в мой нос тут же ударил зловонный запах отходов, стоявший во всём тоннеле. Зажав нос руками, я подошёл к Реду и огляделся по сторонам"
    me "Ну и вонища! Ред, преступник точно бежал сюда? А то мне уже начинает казаться, что здесь ни одно существо не выживет, ужасная вонь стоит!"
    show Red at center with dissolve
    red "Согласен, запашок не из приятных. Ну а что делать, ты представь, что весь город сваливает сюда свот отходы... Да чёрт возьми, здесь любая дрянь может быть!"
    "Ред был недоволен неменьше меня. Однако, останавливаться нам было нельзя. Если мы найдём здесь хоть какие-то следы вора, то это уже будет шаг к успеху"
    me "Ред, как думаешь, куда он мог пойти?"
    red "Не думаю, что ему здесь нравилось больше нас. Это городская канализация, а, как следствие, она имеет выход к морю. Это достаточно недалеко отсюда, думаю, он отправился именно туда"
    red "На самом деле нам нужно быть очень аккуратными... И не только потому, что можно наступить на всякую дрянь. Просто эти канализации создавались не совсем с нуля..."
    me "Не с нуля? Это как?"
    red "Так как Луфтен находится на горе, при его расширении было решено использовать древние пещеры и ходы, сформировавшиеся здесь тысячи лет назад. Сначало это оказалось очень удобным, но власти города не учли один факт..."
    red "Всё это время эти подземные коридоры служили местом обитания самых разных тварей этого мира. Конечно, вначале все они попрятались, испугавшись незванным гостей, но с каждым днём становятся всё наглее"
    red "Учитывая нынешнюю обстановку в королестве, само собой с ними никто ничего делать не хочет, будто и так всё окей. Но когда в один прекрасный день в твою комнату проберётся стая крыс, припомни мои слова"
    me "Да уж, надеюсь такого не произойдёт. Давай лучше поскорее осмотрим эти тоннели"
    scene bg sewage2 with dissolve
    "Мы прошли по длинному коридору примерно в восточном направлении. Хоть за всё это время я и не встретил никого, помимо пары крыс, я будто чувствовал, что целая сотня глаз смотрит нас на со всех сторон"
    "Каждый шаг в этом месте раздавался хлюпающим эхом, каждая капля, падающая с потолка, звучала невообразимо громко. Трудно описать словами, насколько всё-таки ужасно было это место"
    "Как бы я не старался ступать аккуратно, спустя буквально несколько минут прогулки по этой канализации вся моя одежда оказалась необратимо испачкана и пропахла этим едким зловонным запахом"
    "Наконец, мы дошли до конца тоннеля, оказавшись в большом зале с несколькими развилками, ведущими в разные части восточного района города. Здесь мы и остановились"
    red "Слышишь? Это звук морских волн, он доносится из южного тоннеля. Именно туда и стекают все те воды, которые мы наблюдали на протяжении нашего пути"
    me "Да, я отчётливо слышу, как вода ударяется о скалы. В таком случае, нам туда?"
    red "Туда, только подожди чуть..."
    "Ред не успел договорить, как я делаю неосторожный шаг и проваливаюсь по колени в тёмную жижу, растекшуюся по полу!"
    me "Что за?.. Эй, Ред, помоги выбраться!"
    "Я начинаю выкарабкиваться обратно, но в эту секунду что-то хватает меня за ногу и начинает тянуть обратно в зловонную грязь. Подбежавщий Ред пытается вытянуть меня, но его сил явно не хватает..."
    me "Что бы это ни было, я должен от него избавиться! Получи!"
    "Собрав все свои силы в кулак, я вытаскиваю меч и вонзаю чуть дальше своей ноги, постепенно уходящей на дно. В этот момент жуткий визг оглашает всё подземелье"
    "Вокруг меня начинает бурлиться грязь, но я более не чувствую ничего, что держало бы меня. С помощью Реда я вылезаю обратно на камень и смахиваю с себя куски полузастывшых отходов"
    me "Что это было?.. Я чуть... Я чуть не лишился жизни в этом сборище отходов!"
    "Ред, помогавший мне отряхнуться на секунду задумался. Внезапно его глаза начали преобретать кругловатую форму, заполняя большую часть старческого лица"
    red "[me]... Обернись быстрее!"
    image centipede = "images/centipede.png"
    show centipede with fade
    "Прямо за моей спиной выросла огромная туша невиданного мне никогда ранее монстра. Десятки, нет, сотни конечностей заполнили весь мой взор, шевелясь, постепенно подбираясь всё ближе..."
    me "Что это за дрянь?! Ред, ты был в курсе, что такие существа живут в этих стоках?!"
    red "Нет... Может быть... Разве это сейчас так важно?! Берегись!"
    "Гигантская сороконожка нападает на меня, но я вовремя успеваю увернуться. Ред тем временем начинает медленно отсупать в сторону выхода, чтобы не попасть под удары монстра"
    me "Ладно, всего лишь ещё один мерзкий монстр этого мира... Придётся и тебя убить, раз выхода другого нет. Не хочу, чтобы кому-то ещё посчастливилось встретить такую тварь"
    $ renpy.block_rollback()

    define centipede = None

    $ attacks = []
    $ attacks.append(attack("Многоножка делает укус своими жвалами!", std_base_attack, 45, 0)) #base
    $ attacks.append(attack("Многоножка атакует своими когтями!", std_base_attack, 50, 0)) #base
    $ attacks.append(attack("Многоножка набрасывается на вас!", std_base_attack, 40, 0)) #base
    $ attacks.append(attack("Многоножка встаёт на задние лапы и открывает пасть!", std_block_attack, 0, 0)) #block
    $ attacks.append(attack("Многоножка выстреливает в вас едкой кислотой!", std_base_attack, 80, 0)) #after-block
    $ attacks.append(attack("Многоножка начинает оборачиваться вокруг ваших ног!", std_wait1_attack, 10, 0)) #wait
    $ attacks.append(attack("Многоножка вцепляется всеми когтями в ваше тело!", std_wait2_attack, 200, 0)) #after-wait

    $ centipede = enemy("Многоножка", 1000, std_enemy_update, std_enemy_rand, "f")
    $ centipede.attacks = attacks

    $ Player = player(level, xp, std_player_update)
    $ Player.attacks.append(attack("Молниеносный удар", lightning_attack, value = Player.max_damage, cost = 2))
    $ Player.attacks.append(attack("Смертельный вихрь", tornado_attack, value = Player.max_damage, cost = 2))

    $ Log = log(std_win_check, std_lose_check, std_log_update, "Начался бой с многоножкой!")

    call screen fight_screen(Log, Player, centipede)

    $ newLv = Player.add_xp(600)
    $ level = Player.level
    $ xp += 600 #2600 / 2800 | default: 2100 / 2800

    $ renpy.block_rollback()

    "Вы получаете 600 ед. опыта!"
    if newLv:
        "Ваш уровень повышен до [level]!"
    hide centipede
    "я толкаю тушу многоногой твари и скидываю её в в грязевую воду. Булькнув, тело скрывается в недрах резервуара"
    me "Фух, ну и гадость... Ред, можешь выходить, всё чисто!"
    show Red with dissolve
    red "[me], да ты и в правду делаешь успехи! Увидев эту тварь, я уж было подумал, что всё кончено... Но ты разделался с ней даже не моргнув, поздравляю!"
    me "Не стоит благодарности, я мог бы и лучше, но вот, меч не позволяет, к сожалению"
    red "Понимаю, но других орудий у нас пока нет. Будут деньги - зайдём на рынок и купим новый, по твоему усмотрению"
    me "Было бы классно. Ну что же, пошли тогда дальше, надеюсь далее будет без происшествий"
    hide Red with dissolve
    "Наш поход по глубинам подземелья продолжился. Но теперь с каждым шагом на юг, я чувствовал, что воздух становился чуть-чуть легче, всё сильнее ощущалось влияние моря"
    "Словно чуя, что темнота и рассеваивается, попряталась и вся подземная живность, на её смену пришли наземные насекомые, обустроившие свои гнёзда в прохладном тоннеле канализации"
    scene sewage3 with dissolve
    "И вот, о чудо! Мы наконец покинули эти невыносимые стоки, оказавшись в небольшой пещере с попадающими в неё с разных сторон трубами"
    "Ослепительный свет заходящего солнца играл на земле пещеры, звук волн моря раздавался эхом, отскакивая от каменных сводов бесчисленное число раз"
    "Но нельзя забывать, зачем я и Ред прошли весь этот путь. Рано радоваться, преступник ещё не найден, а значит наша массия не окончена"
    show Red with dissolve
    me "Давай осмотрим эту пещеру. Раз ты считаешь, что он вышел сюда как и мы, то дальше идти ему было некуда. Я посмотрю вон тот дом на возвышении"
    red "Без проблем, на меня тогда вся оставшаяся часть. Если что - дай знать, я постараюсь помочь"
    hide Red with dissolve
    "Недолго думая, я начал подниматься в сторону полуразвалившейся конструкции с поломанной черепичной крышей. Уже тогда я начал слышать какие-то неестественные звуки..."
    me "Эй, кто здесь?! Выходи, я знаю, что ты там, внутри! Если сдашься мирно, то обещаю, я сохраню твою жизнь!"
    "В доме упало нечто стальное на пол. Затем раздался топот ног и на пороге появился странный человек в лохмотьях и боевым ножом в руке. Лицо его было укрыто грязной тканевой повязкой"
    show rogue3 with fade
    "Разбойник: " "Кто ты?! Проваливай отсюда, пока я тебя не прикончил! У тебя пять секунд, чтобы это сделать, иначе я совсем разозлюсь!"
    me "Постой, я не хочу с тобой драться. Ты, как понимаю, тот самый преступник, что украл деньги людей из банка. Верни их, и, думаю, мы сможешь договориться..."
    "Разбойник: " "Чёрта с два я стану тебя слушать! Сейчас ты поплатишься за то, что пришёл в чужой дом без стука!"

    define rogue3 = None

    $ attacks = []
    $ attacks.append(attack("Разбойник атакует своим кинжалом", std_base_attack, 30, 0)) #base
    $ attacks.append(attack("Разбойник прыгает на вас, ударяя ногой!", std_base_attack, 20, 0)) #base
    $ attacks.append(attack("Разбойник кидает в вас ближайший камень", std_base_attack, 10, 0)) #base

    $ centipede = enemy("Разбойник", 250, std_enemy_update, std_enemy_rand)
    $ centipede.attacks = attacks

    $ Player = player(level, xp, std_player_update)
    $ Player.attacks.append(attack("Молниеносный удар", lightning_attack, value = Player.max_damage, cost = 2))
    $ Player.attacks.append(attack("Смертельный вихрь", tornado_attack, value = Player.max_damage, cost = 2))

    $ Log = log(std_win_check, std_lose_check, std_log_update, "Начался бой с разбойником!")

    call screen fight_screen(Log, Player, centipede)

    $ newLv = Player.add_xp(200)
    $ level = Player.level
    $ xp += 150 #2800 / 3600 | default: 2300 / 2800

    $ renpy.block_rollback()

    "Вы получаете 150 ед. опыта!"
    if newLv:
        "Ваш уровень повышен до [level]!"
    "Разбойник: " "Что... Когда ты... Успел..."
    hide rogue3 with dissolve
    "Не успел приступник моргнуть и глазом, как я совершаю серию ударов и оставляю его с разрезанными сухожилиями на земле, не в силах двигаться"
    "Подоспевший Ред уже застал меня, протирающего свой меч над ещё живым, но сильно раненым преступником, бормотавшим бесчисленные проклятия в мой адрес"
    me "Очень глупо было лезть в бой, не зная своего врага. Раз уж ты не захотел по-хорошему, то будет по-плохому. Говори, куда спрятал украденные деньги!"
    show Red at right with moveinright
    show rogue3 at center with moveinbottom
    "Ред помог разбойнику подняться и, поднеся его же нож к горлу, дал преступнику знать, что настал его черед слушаться нас"
    "Разбойник: " "Деньги... В доме, под половицами... Я не тратил их, только вчера украл. Отпустите... Гх... меня, я всё верну, только оставьте в живых"
    "На удивление преступник не стал мне долго сопротивляться и сразу же сознался в содеянном. У меня даже возникли сомнения, всё ли тут чисто..."
    me "Ред, сходи в дом и узнай, правду ли говорит этот преступник. Я пока поговорю с ним наедине"
    red "Как скажешь, только не упусти его. Я мигом!"
    hide Red with fade
    "Ред оставил нас одних с преступником, всё ещё находившимся в полуобморочном состоянии. Хоть кровь и капала с его ног, я пока что не стремился помогать этому человеку"
    me "Я надеюсь ты ещё в состоянии ответить на мои вопросы и готов к сотрудничеству. Перед тем, как убить тебя или сдать властям, очень хотелось бы узнать от тебя ответы на пару вопросов"
    "Разбойник еле кивнул головой в знак своего согласия. Я же продолжил..."
    me "Первый вопрос: Ты сам решил украсть деньги или тебя кто-то заставил. Сразу говорю, обманешь - умрёшь"
    "Разбойник: " "С-сам, я сам решился их украсть..."
    me "В таком случае задаю второй вопрос: Зачем ты это сделал? Жажда наживы, месть, голод или что-то ещё?"
    "Преступник на секунду замялся, будто не зная, что ответить на мой вопрос. Но, видя, как я начинаю доставать свой меч, он решился дать ответ..."
    "Разбойник: " "Нищета... Ничто иное как голод и бедность заставляет людей совершать такие поступки. Я не искл... Гх... исключение"
    "Разбойник: " "Живя в таком месте, волей-неволей придёшь к тому, что единственный способ выжить - убить или ограбить кого-то. Не хочу перед тобой оправдываться, но я это сделал не от хорошей жизни"
    me "Это не повод! Разве можно... Разве можно так поступать, зная, что от этого будут страдать другие? Думаешь, нет другого пути?"
    "Разбойник: " "Нет! Нет другого пути... Тебе легко говорить, ты небось никогда и не был в том положении, в котором я находился всю свою жизнь, откуда тебе вообще хоть что-то знать?!"
    me "Быть может. Но твой поступок всё равно невозможно назвать правильным. Мне придётся дать тебя страже, они и определят, что с тобой делать..."
    "Разбойник: " "Убьют они меня, что ты таишь, будто сам не знаешь... Пощади, если в душе что-то осталось! Обещаю, я более не стану грабить, сдохну, но не стану!"
    me "Трудно мне тебе верить, непросто это... Да и решать я права по-хорошему не имею. Так или иначе..."
    define rogue_killed = False
    menu:
        "сдать преступника страже":
            $ rogue_killed = True
            me "Что с тобой делать, решит стража, я никому не судья. Человек, вступивший однажды на тёмный путь, оттуда не возвращается"
            "Разбойник закрыл глаза и опустил голову к земле. Упав на колени, он протянул мне руки, чтобы я мог их связать"
            "Вскоре подоспел и Ред с мешком денег на плечах. Радости его не было предела, хотя я же всё никак не мог понять, чему тут радоваться..."
        "пощадить преступника":
            me "Я всё же решил пощадить тебя. Может, это будет самой большой ошибкой за всю мою жизнь, но мне тяжело игнорировать твою судьбу. Вот тебе повязка для ран, ты свободен"
            "Разбойник: " "Что... Ты правда... Меня пощадишь и отпустишь? Просто так?"
            me "Тебе нечего мне предложить, ступай прочь, пока я не передумал! Живо!"
            "Ред стоявший всё это время на холме, наконец спустился вниз, видя как разрешилось дело. На его плечах я заметил большой мешок со звонкими монетами"
    hide rogue3 with dissolve
    show Red with dissolve
    red "Ну что, идём получим награду за проделанную работу! Давай, [me], потарапливайся, незачем задерживаться в таком угрюмом месте!"
    me "Да, ты прав Ред, идём отсюда поскорее, я и сам не прочь покончить со всем этим, устал я..."
    hide Red with dissolve
    if rogue_killed:
        "Я взяв конец веревки, который был связан преступник. Он не дергался, нет, наоборот, был необычайно спокоен, словно всё для него наконец закончилось"
    "Мы пошли к выходу на морское побережье. Затем, поднявшись по скалистой дороге, вернулись обратно в восточный район, в тот самый сквер, где наш ждал банкир вместе со своей стражей"
    scene bg luften5 with dissolve
    show guardian_left at left
    show guardian_right at right
    show banker at center
    banker "Кого я вижу! Ред, [me]! Вы правда справились с заданием и вернулись в полном составе из этого зловонного подземелья! Да с мешком денег, какие молодцы!"
    me "Да, здесь все деньги, что были украдены вором прошлой ночью, возможно, немного было утеряно, но нашей виной такое вряд ли назовёшь"
    banker "Понимаю вас. А что насчёт самого преступника? Нашли его? Убили?"
    if rogue_killed:
        me "Вот он, забирайте под стражу. Пришлось с ним драться, так что если оставите в живых, обработайте раны на его ногах"
        "Стража взяла под руки разбойника и, взяв из моих рук верёвку, увела в сторону входа в банк"
    else:
        me "К сожалению, найти его не удалось, мешок с деньгами был спрятан в каких-то развалинах, но следов человека там не было. Впрочем, его поиск и не был нашей целью, насколько помню"
        banker "Да, жалко, конечно, что он не сможет ответить перед законом, но думаю, это в действительности работа уже не для вас, а для стражи. Главное - деньги при вас"
        "Банкир махнул рукой страже, дав знать, что делать ей здесь более нечего. Покопавшись, воины скрылись за дверьми банка, оставив нас наедине"
    hide guardian_left with moveinleft
    hide guardian_right with moveinright
    "Я передал банкиру тяжеловестный мешок со всем его содержимым. Взамен более мелкий мешочек и грамота оказались в моих руках"
    banker "Конечно, денег тут в разы меньше, но, думаю, этого в награду будет достаточно. Грамота за успешное выполнение также прилагается. Спасибо и удачи вам, путешественники!"
    "Банкир протянул нам в руку в знак благодарности. Ред и я поблагодарили его в ответ. Да, мы конечно могли оставить все деньги себе, но чем бы мы тогда были лучше того преступника?"
    me "И вам спасибо. Зовите, если что ещё нужно будет, с радостью поможем, наша работа как никак. Но, кажется, уже темнеет, мне и Реду стоит идти. Прощайте!"
    hide banker with dissolve
    "Банкир помахал нам рукой и также скрылся в большом мраморном здании. Нам же с Редом предстояло вернуться в гильдию, чтобы решить, что делать дальше, когда квест был наконец выполнен"
    jump luften_quests1

label luften_night:
    $ stage = "Особняк Йозефа"
    $ save_name = "Глава " + str(chapter) + ". " + stage
    scene bg luften2 with dissolve
    show Red at center
    red "Уже темнеет, думаю, стоит вернуться к Йозефу и отдохнуть перед завтрашним днём"
    me "Согласен... Я и сам ужасно вымотался за этот день, столько всего произошло!"
    red "Да, встреча с сэром Штрауфом, путешествия по ужасным тоннелям канализации... Брр, вспоминать даже не хочется"
    red "Однако, мы собрали достаточно много денег, [me]. У меня в карманах так и чувствуется звон этих чудесных блестящих монет!"
    red "Думаю, тут в районе десяти золотых. Иначе говоря, мы покрыли наши расходы за последнюю неделю сполна"
    red "Завтра пойдём на рынок и купим тебе новый меч, а заодно и припасы в виде еды и зелий. Они нам пригодятся"
    scene bg joseph_house1 with dissolve
    "К сумеркам мы были уже на пороге дома Йозефа. При свете фонарей, сидя на небольшой приусадебной скамейки, граф читал какую-то книгу, медленно перебирая страницы своими руками"
    show Joseph with dissolve
    joseph "Рад вас снова видеть, друзья. Каковы же ваши успехи, что нового повидали за этот прекрасный лентий день?"
    show Red at right with moveinright
    red "Словами не передать, Йозеф! Это был такой день, словно я неделю пережил! Главное вот что - деньги у нас теперь есть"
    joseph "Приятно это слышать, Ред. Ну чего же вы тогда ждёте, проходите в дом поскорее, уже смеркается, темно совсем становится"
    hide Joseph with fade
    hide Red
    "Йозеф отворил дверь своего поместья и пригласил нас внутрь. Скинув ненужные вещи, мы с Редом проследовали туда и уселись за обеденный стол в гостинной, чтобы рассказать всё с нами произошедшее"
    scene bg joseph_house2 with dissolve
    show Joseph
    joseph "То есть выхотите сказать, что повстречали некоего сверхсильного воина-мага по имени Ваал, пришедшего в Луфтен, чтобы украсть какую-то посылку? Всего лишь маленькую шкатулку, так?"
    me "Именно так, господин Йозеф! Если бы не сэр Штрауф, находившийся в то время со своей стражей у ближайшего трактира, то скорее всего мы бы больше вообще не встретились!"
    joseph "Хорошо, в таком случае, что было в этой посылке, откуда вы её вообще взяли?.."
    me "Ред нашёл её после того, как уехал крестьянин Джоун. Видимо как раз он её и обронил. Быть может, это была одна из тех посылок, которые он доставлял между деревнями до того, как повстречал нас"
    me "А что внутри... Понятия не имею. Я отдал её Штрауфу, после той битвы это было единственно правильное решение. Ключа от неё не было, да и вообще я предполагал, что просто отдам её владельцу и дело с концом"
    joseph "А владелец был таинственным образом убит... Скорее всего тем самым Ваалом. Ну что же, ситуация почти что ясна мне. Единственное, вы пробовали искать Джоуна? Вдруг он что знает, но молчит?"
    me "Это не исключено, но пока что для нас его поиски будут весьма затруднительны, к тому же, он может быть уже даже не в Луфтене вовсе. Но идея неплохая, через него можно выйти на отправителя шкатулки, если подумать"
    joseph "Вам стоит этим заняться, думаю, я смогу помочь в этом деле. К слову, сама шкатулка до сих пор у Штрауфа? В королевском дворце?"
    me "Полагаю, что да. Во всяком случае так сказал сам Штрауф, когда удалялся со своим отрядом после сражения. Я кстати так и не показал ему тот осколок кабаньей чешуи, что мы принесли из деревни Криа"
    hide Joseph with dissolve
    "Йозеф облокотился на спинку кресла и посмотрел куда-то в сторону. Сидевший в стороне Ред также давно уже дремал, совершенно забыв о всех наших проблемах. Да и сам я уже начал чувствовать сковывающий меня сон..."
    scene bg guesthouse_room1 with dissolve
    "Приподнявшись из-за стола, я направился наверх в спальню. Прошагав по старой деревянной лестнице, я бухнулся на свою кровать и погрузился в глубокий сон..."
    scene bg dark_village with fade
    $ stage = "Воспоминания"
    $ save_name = "Глава " + str(chapter) + ". " + stage
    me "Деревня..."
    me "Где я?..."
    me "Это сон?.."
    "Я стоял в шелестящей от ветра траве, в поле, перед неизвестной мне ранее деревней"
    "Тёмные, грозовые облака заполняли почти все небо над моей головой, казалось, будто сейчас глубокая ночь"
    "Я сделал несколько шагов в сторону деревни. Вдали были слышны какие-то крики, еле-еле, словно эхо"
    "До моего запаха донёсся запах горящего дерева. Я попытался шагнуть вперёд. Но ноги не шевелились..."
    if not duel_won:
        "Вдруг я заметил, как нечто странное коснулось моей спины. Обернувшись, я увидел нечто странное, даже можно сказать, страшное"
        image dark_knight = "images/dark_knight.png"
        show dark_knight with fade
        "Практически неразличимый во тьме, передо мной стоял рыцарь, одетый в странные чёрные доспехи. Не успел я сделать и шаг, как длинная секира полоснула меня по плечу!"
        "Вы получаете 50 ед. урона!"
        "Чёрт, медлить было нельзя! Нащупав свой меч у бедра, я обнажил клинок, приготовившись отразить следующий наступающий удар..."
        $ renpy.block_rollback()

        define dark_knight = None

        $ attacks = []
        $ attacks.append(attack("Рыцарь делает сквозной удар!", std_base_attack, 50, 0)) #base
        $ attacks.append(attack("Тёмный рыцарь атакует своими когтями!", std_base_attack, 45, 0)) #base
        $ attacks.append(attack("Рыцарь напрыгивает на вас с мечом!", std_base_attack, 45, 0)) #base
        $ attacks.append(attack("Тёмный рыцарь концентрирует энергию...", std_block_attack, 10, 0)) #block
        $ attacks.append(attack("Тьмя окутывает всё вокруг!", std_base_attack, 90, 0)) #after-block
        $ attacks.append(attack("Рыцарь блокирует входящие атаки мечом...", std_wait1_attack, 0, 0)) #wait
        $ attacks.append(attack("Тёмный рыцарь парирует ваш удар!", std_wait2_attack, 150, 0)) #after-wait

        $ dark_knight = enemy("Тёмный рыцарь", 900, std_enemy_update, std_enemy_rand)
        $ dark_knight.attacks = attacks

        $ Player = player(level, xp, std_player_update)
        $ Player.attacks.append(attack("Молниеносный удар", lightning_attack, value = Player.max_damage, cost = 2))
        $ Player.attacks.append(attack("Смертельный вихрь", tornado_attack, value = Player.max_damage, cost = 2))
        $ Player.health -= 50

        $ Log = log(std_win_check, std_lose_check, std_log_update, "Начался бой с тёмным рыцарем!")

        call screen fight_screen(Log, Player, dark_knight)

        $ newLv = Player.add_xp(500) #2800 / 3600
        $ level = Player.level
        $ xp += 500

        $ renpy.block_rollback()

    "Вы получаете 500 ед. опыта!"
    if newLv:
        "Ваш уровень повышен до [level]!"

    scene bg guesthouse_room1 with fade
    $ stage = "Особняк Йозефа"
    $ save_name = "Глава " + str(chapter) + ". " + stage

    "Я проснулся ближе к обеду, ощущая ужасный голод в своем желудке, будто вся вчерашняя еда была съедена не мной, а кем-то иным"
    "Что же это было? Сон? Видение? Моё прошлое? Почему так картина до сих пор будто оставалась перед моими глазами?"
    "Я встал с кровати и умылся водой из фляги. Затем, одевшись, вышел из комнаты в коридор второго этажа"
    scene bg joseph_house2 with dissolve
    "Спустившись по лестнице вниз, я заметил, что ни Реда, ни Йозефа уже нет дома, а дверь на улицу открыта, принося в помещение букет запахов с улицы"
    scene bg joseph_house1 with fade
    "Они стояли на улице, о чём-то громко споря. До меня то и дело доносились ругательства Реда, что-то объясняющего своему товарищу"
    "Однако, как только я подошёл ближе, всё стихло, и два взора устремились на меня, спустившегося на лужайку"
    show Red
    red "Привет, [me], ты я вижу уже проснулся и снова готов к путешествиям?"
    me "Скорее всего, смотря какие у нас на сегодня планы... Кстати, о чём вы сейчас спорили?"
    red "Да так, мелочи жизни. Не бери в голову. Йозеф, я думаю, мы уже должны идти. Скорее всего снова вернёмся к вечеру, так что не переживай сильно"
    hide Red with dissolve
    show Joseph with dissolve
    "Ред ушёл за вещами, оставив меня вдвоём с Йозефом. Граф стоял, нервно постукивая пальцами по спинке садовой скамейки"
    joseph "Будьте аккуратны, [me]. С каждым днём в городе становится всё опасней, старайтесь не натыкаться почём зря ни на кого"
    "Йозеф явно был взволнован, к тому же, по видимому из-за меня. Что же случилось..."
    me "Я понимаю, господин Йозеф, но по другому никак. Битв не избежать, хоть я и стараюсь. Я же всё ещё жив как никак"
    joseph "Да, но твой рассказ про вчерашнюю схватку Штрауфа и Ваала заставил меня задуматься. Лучше тебе более не встревать в такие передряги"
    me "Я постараюсь, господин Йозеф, постараюсь. Однако, сейчас нам пора уже идти, Ред ждёт у выхода, как я вижу"
    if duel_won:
        joseph "Да... Ну что же, идите, буду ждать вас к вечеру, живыми и невредимыми"
    else:
        joseph "Да... К слову, [me], возьми вот этот маленький подарок от меня... Это старый талисман моей семьи, по легенде он защищает носителя от любых опасностей"
        "Йозеф протянул мне в руки маленький ключик на верёвочке, украшенный красным драгоценным камнем посередине"
        "Видя его настойчивый взгляд, я не стал возражать и принял подарок"
    me "Благодарю вас, Йозеф, но теперь точно стоит идти. До скорых встреч!"
    scene bg luften_market with dissolve
    $ stage = "Рынок Луфтена"
    $ save_name = "Глава " + str(chapter) + ". " + stage

    "Мы вышли с Редом на городскую улицу и направились в сторону Луфтенского рынка. Благо, народу сегодня было не так много и дорога туда была весьма лёгкой"
    me "Думаю, нам стоит перво-наперво купить меч, мало ли что случится, а, Ред?"
    show Red with dissolve
    red "Да-да, без проблем, выбирай, какой душе угодно, только в пределах нашего бюджета. А эту ржавую железяку выкинем прочь"
    "Я остановился у одной из оружейных лавок рынка и начал осматривать здешние товары. Дороговаты они, однако!"
    me "Хм, вроде этот меч не плохой и сделан из серебра. Для монстров подходит. И цена приемлемая"
    hide Red
    show banker with fade
    "Торговец: " "Сэр, вам помочь с выбором? Хотите этот меч? Сделаю для вас специальную скидку!"
    me "Звучит конечно очень заманчиво. А сколько в таком случае будет стоит это оружие?"
    "Я взял с полки новый, длинный, блестящий меч и протянул его продавцу. Тот внимательным образом начал его осматривать"
    "Торговец: " "Двенадцать золотых! Продаю за каких-то жалких двенадцать монет!"
    "Я пристально посмотрел на торговца, недовольно покачивая своей головой. Мужчина, заметив, что на такую цену я идти не хочу, быстро переменился в лице"
    "Торговец: " "Ладно, шучу! Продаю за десять, скидка, как и обещал! Не сердитесь, сэр!"
    me "То-то же. Ладно, беру за десять вот этот меч, так уж и быть. Надеюсь, гарантия хоть будет?"
    "Торговец: " "Всё будет, обещаю! Меч долго прослужит, он видите какой, серебром покрытый, не заржавеет!"
    hide banker with dissolve
    "Я подозвал Реда к лавке и попросил его отсыпать мне десяток монет из нашего общего \"банка\". Торговей с радостью принял мою оплату и отдал мне новый меч, вместе со специальными для него ножнами"
    show Red with dissolve
    "Только взяв товар в свои руки, я почувствовал, как необычайная сила придала мне уверенности. Не знаю, в чём был секрет, но это событие явно было переломным в моей карьере!"

    $ newLv = Player.add_xp(1000) #3800 / 4500
    $ level = Player.level
    $ xp += 1000
    $ renpy.block_rollback()

    "Вы получаете 1000 ед. опыта!"
    if newLv:
        "Ваш уровень повышен до [level]!"

    me "Да, теперь мне точно ничто не будет мешать становлению настоящим воином! Я прямо чувствую ту мощь, которую заложил кузнец этого орудия в своё творение!"
    red "Очень рад, что тебе подходит этот меч. К тому же, пока ты тут копался, я сходил в лавку напротив и прикупил несколько лечебных зелий и даже усилений на чёрный день"
    red "Стоит отметить, что чем дальше мы заходим, тем сильнее становятся наши враги. Случай с тем монстром в деревне Криа был показательным - иногда без зелий не обойтись"
    me "Полностью согласен, Ред. Давай тогда купим ещё еды на дорогу, раз уж на рынке оказались. Больно не удобно питаться два раза в день!"
    hide Red with dissolve
    "Ред кивнул в знак согласия и повёл меня в строну продуктовых лавок. Благо, денег теперь у нас было достаточно, чтобы обзавестись едой на недели вперёд"
    "Купив несколько ломтей хлеба, вяленого мяса и фруктов про запас, дела наконец-то были завершены. Съев по свежайшему бутерброду с приобретённой едой, мы снова были готовы к свершениям!"
    scene bg luften2 with dissolve
    show Red
    "Мы стояли в западном районе Луфтена на той самой дороге, по которой когда-то приехали в столицу королевства. Сколько времени прошло с тех пор? Всего лишь несколько дней?"
    "У нас ещё оставалась пара квестов про запас, но я чувствовал, что нельзя тянуть с более важным делом. То, зачем мы так скоро приехали в этот город... Тот кровавый и таинственный трофей, доставшийся после убийства кабана"
    me "Слушай, Ред, я вот что вспомнил. Кусок чешуи, что мы взяли с собой из деревни Криа. Нужно срочно донести его до сэра Штрауфа и попыться узнать, откуда такой мощный монстр смог появится и как он уничтожил целую деревню"
    me "Я говорил на этот счёт с Йозефом, он также рекоммендовал скорее найти генерала армии и передать ему это. Так что боюсь, наши задания придётся отложить на потом"
    "Ред выслушал мою речь и опять нахмурил свои старческие седые брови. Ему явно было крайне лень заниматься этими вещами, но видя мою настоячивость, старик согласился"
    red "Да, надо заняться этим делом. Только вот одна проблема... Луфтенский дворец находится высоко на горе, да и окружён он кучей стражи, через которую не так-то просто пройти. Даже по такому важному делу, как тебе кажется"
    me "Но мы всё равно должны! К тому же сэр Штрауф уже знаком с нами, он обязательно послушает меня и тебя!"
    red "Эх, ну что с тебя взять... Ну может и так. Ладно, я знаю примерную дорогу, идём, покажу как пройти до королевского дворца"
    scene bg luften1 with dissolve
    "Ред повёл меня по центральной городской улице прямо в гору. Дорога, конечно, эта, была была не из лёгких!"
    "Чтобы хоть как-то скоротать время, Ред снова принялся рассказывать своим многочисленные истории, приобретённые за те долгие годы его странствий по миру Инзеля"
    red "Что-ж, дворец Луфтена - это огромный, просто невообразимых размеров собор, находящийся на самой верхушке, можно сказать на пике Северной Горы"
    red "Часть собора открыта для публики в дневное время суток, часть - только для короля, его семьи и приближённых. К ним относится и сэр Штрауф, проживающий в одном из крыльев центрального здания, рядом с королевским горнизоном"
    red "К числу открытых областей этого комплекса относится к примеру королевский сад - большая открытая оранжерея на небольшом плато, открывающаяся прямо на Луфтенский порт и океан Инзеля"
    red "По праздникам в саду могут устраивать открытые пиршества, на которые могут прийти все местные жители, а иногда даже приезжие. На них присутствует и император Эрлих II, правда в такое время к нему и не подступиться"
    red "К слову, императора можно встретить и в обычный солнечный день, прогуливающегося по саду в составе своей семьи и телохранителей из горнизона"
    red "Ходят слухи, что в такие дни к нему даже можно подойти и задать интересующие вопросы, но верится в это конечно слабо"
    me "И на него никто не пытался напасть? Всё-таки, сейчас многие недовольны обстановкой в городе, не стоило ли правителю такого большого королевства быть более осторожным?"
    red "Нападали, но с ними быстро расправлялись. Ты же как никак видел силу сэра Штрауфа, не зря его же назначили главнокомандующим армии! Он быстро расправлялся с такими преступниками!"
    red "Но народу конечно в будние дни бывает не много. Идти долго всё-таки, да и вся движуа скорее будет происходить на центральной площади у гильдии, нежели у королевского дворца"
    red "Я и сам был там пару раз. И то на новогодние праздники, когда практически каждый уходит из города ко дворцу. Знаю только, что на аудиенцию к Эрлиху попасть достаточно проблематично"
    scene bg luften_gates with dissolve
    $ stage = "Королевский дворец"
    $ save_name = "Глава " + str(chapter) + ". " + stage

    "Ред и я шли так ещё где-то час, пока наконец не оказались на самой вершине, перед огромными воротами, окруженными стражей, верно державший свой пост"
    "Видимо, чем ближе воины к императору, тем лучше они справляются со своими обязанностями. Но сейчас меня волновало не это. Вопрос был скорее в том, как попасть внутрь замковой территории?"
    "Я подошёл к одному из стражников, что стояли на посту, чтобы узнать, как пройти внутрь"
    "Не смотря на то, что они всем видом показывали своё нежелание с кем-либо говорить, я всё же заставил их обратить на меня внимание"
    show guardian_left at left with moveinleft
    show guardian_right at right with moveinright
    "Стражник: " "Что нужно? Вход во дворец сегодня закрыт, сейчас тут проходит день совещаний в городском совете"
    me "Мне хотелось бы встретиться с сэром Штрауфом по одному очень важному и личному делу. Очень желательно - сегодня"
    "Стражник: " "Сэр Штрауф также находится на совещании и не сможет вас сегодня принять. Приходите в другой день... Приходите в выходные"
    me "Выходные?! Сейчас только начало недели! Кто у вас тут может передать, что за воротами дворца Штрауфа просит [me] и Ред?"
    "Стражник: " "Никто. У нас смена поста по расписанию ближе к вечеру. Если нужно что-то передать, приходите..."
    "Видя это явное наплевательское отношение, я чуть было не обнажил свой новый меч. Однако, что-то в тот момент случилось с часовым..."
    "Стражник: " "Хорошо, хорошо, я пойду и передам прямо сейчас. Но учтите, что если генерал не откликнется на вашу просьбу о встрече, то пеняйте на себя!"
    "Стражник покинул свой пост и направился через башню в сторону центрального собора, оставив нас с Редом с ещё несколькими воинами"
    hide guardian_left with moveinleft
    me "То-то же. Вот тебе и демократия, надо сразу было настойчивее быть с ними..."
    "Я присел на скамейку и положил свои вещи рядом, ожидая возвращения стражника. К счастью, он не заставил себя долго ждать..."
    "Я услышал звонкие удары доспехов об каменную мостовую. Ещё мгновение, и из-за ворот вышел сам сэр Штрауф, облаченный в свои боевые доспехи"
    show Shtrauf with fade
    shtrauf "Ред, [me], приятно увидеть вас живыми. Надеюсь то дело, за которым вы сюда пришли, действительно важно"
    me "Скорее всего так... Только, я бы не хотел говорить о таких вещах на улице. Можно как-нибудь пройти внутрь и обсудить всё в помещении?"
    "Мой вопрос немного сбил Штрауфа с мыслей, однако он быстро дал на это согласие и открыл замковые ворота для меня с Редом"
    "Стража никак не стала перечить приказу командира и мгновенно пропустила нас внутрь собора, сразу в западное его крыло, где располагался приёмный зал"
    scene bg luften_palace with dissolve
    show Shtrauf
    "Сэр Штрауф прошёл за нами в огромную мраморную комнату с высокими потолками и закрыл входную дверь на ключ"
    "Не снимая брони и даже шлема, он уселся на ближайший диван и поставил свой меч рядом с собой, заодно пригласив нас сесть напротив"
    me "Благодарю, сэр Штрауф. Надеюсь, мы не отнимем у вас много времени и вы сможете вернуться к вашим более важным делам"
    shtrauf "Глупости, совещание уже закончилось, так что я весь во внимании. Выкладывайте, зачем пожаловали во дворец так скоро после последней встречи"
    "Я молча достал из сумки кусок каменной чешуи и положил на небольшой столик перед генералом. Тот заинтересованно подвинулся ближе к этому трофею"
    shtrauf "И что же это вы принесли? Кусок камня? Или же..."
    "Сэр Штрауф замялся и медленно коснулся лежавшего на столе куска чешуи. Затем поднял взгляд на меня и Реда"
    me "Этот предмет - останки монстра, которого мы убили неделю назад в деревне Криа, к северо-востоку от столицы Луфтена. Я не сообщил вам ранее, так как обстоятельства не позволяли"
    "Штрауф молча смотрел мне в глаза несколько секунд, словно убеждаясь, что я говорю правду. От такого напряженного взгляда мне даже стало чуточку не по себе"
    shtrauf "Неделю назад... От этого предмета до сих пор исходит мощный магический заряд... Как будто Оно было живым совсем недавно... Как такое возможно?"
    me "Мы бы и сами хотели знать. Энергия в нём уже чуть слабее, чем после сражения, но сохраняется достаточно хорошо. Предположительно, это из-за происхождения убитого монстра"
    shtrauf "Что это был за монстр... Опишите мне его как можно подробнее! Если окажется, что это как-то связано с... Впрочем, вам стоит начать, не буду раскрывать лишнего"
    me "Хорошо, как скажете, сэр Штрауф. Этот кусок каменной чешуи принадлежал огромному кабану размером с чуть ли не с деревенский дом. Мы повстречали его, как только собирались уехать из заброшенной деревни на окраине столицы"
    me "Мне кажется, именно он и послужил причиной бегства оттуда всех жителей. К слову, в одном из домов я нашёл одно испорченное пиcьмо, адресованное некоему капитану Тунру. Вы с ним знакомы?"
    shtrauf "Капитан Тунр? Капитан Тунр... Да, вроде как я его помню... Этот человек руководил южным горнизоном последние лет десять. Это на границе Луфтена с Мариэном, километров тридцать от столицы"
    shtrauf "Что же было в этом письме? Какое-то поручение?"
    me "Просьба встретиться с племянником одного из жителей в столице, насколько я запомнил. Но вряд ли послание дошло до получателя, учитывая, в какой спешке бежали местные жители из Криа"
    me "Я ещё не успел никому об этом рассказать, поэтому знаю не больше вас. Не уверен даже, важно ли это письмо, учитывая то, с чем мы столкнулись после этого"
    shtrauf "Хорошо, но если этот... кабан... был настолько мощным, то как же вам удалось его одолеть? В нём должна была храниться огромная магическая энергия, учитывая силу только одного осколка чешуи!"
    me "Не знаю... как-то вот так. Может, чисто моё везение. Может, он уже был ранен... Сэр Штрауф, у вас есть предположения относительного этого предмета?"
    shtrauf "Я могу попробовать кое-что узнать. Правда, для этого придётся высвободить ту магическую энергию, что осталась в чешуе. Такой анализ даст понять примерное происхождение того создания"
    "Штрауф снова наклонился над осколком и положил правую руку поверх него. Другой рукой рыцарь дал нам знак отойти подальше от предстоящего места исследования"
    shtrauf "Если это сделал человек, волей-неволей ему пришлось оставить некоторую метку, инициализирующую хозяина. Иначе монстр бы просто напал на него. В таком случае, мы сможем услышать \"отголоски\" заклинания"
    me "Отголоски?"
    shtrauf "Да, именно. Если всё пойдёт как надо, мы поймём, где находился хозяин в момент сотворения того монстра. Так что приготовьтесь!"
    shtrauf "Снятие магической печати! Пятый уровень! Воссоздать изначальное строение элемента!"
    "Штрауф занёс вторую руку над осколком и яркое голубое пламя загорелось в его перчатке. Затем последовал хлопок и комнату озарило ярчайшее сияние, и тут же мощный порыв ветра откинул меня в сторону"
    scene bg dark_village with fade
    show Shtrauf
    show Red at right
    red "Что за... Какого чёрта?! Как мы оказались в поле?!"
    "Необычная энергия выбросила нас троих на то самое поле из моего сна, только теперь всё было абсолютно тихо, словно уже давно мёртво. Я смог нащупать под собой меч и встать на ноги, затем помог сделать это же Реду"
    "Сэр Штрауф молча стоял и осматривал территорию, словно ища кого-то. Даже не вздрогнув, воин будто знал заранее, что мы окажемся здесь"
    me "Господин Штрауф... Что это за место? Вы знаете его?"
    shtrauf "Знаю, [me], знаю. Это деревня Дарг, очень старое место... Неужели, именно здесь был создан тот самый монстр? В месте, следы которого уже давно стёрты?"
    me "Подождите, что значит нет? Разве сейчас мы не находимся прямо здесь?"
    shtrauf "Нет конечно, это лишь иллюзия, которую создаёт заклинание снятия печати в комбинации с высвобожденной энергией. То, что ты видишь вокруг, давно уже перестало существовать. Если быть точнее, уже как несколько лет"
    "Сэр Штрауф сделал несколько шагов вперёд и вонзил свой меч Глубоко в мёртвую почву. И вот, снова раздаётся хлопок, порыв ветра..."
    scene bg luften_palace with fade
    show Shtrauf
    shtrauf "Я видел достаточно. Кто бы мог подумать, что наш мир настолько тесен..."
    "Я стоял рядом с Редом и смотрел на спокойно садящегося за стол рыцаря. Мягко говоря, все эти события оказались для меня шокирующими. Я почти не соображал, что только что произошло, как, впрочем, и Ред"
    "То место... Я видел его в своих снах... Или это было не оно? Стоит об этом говорить Штрауфу? Может быть, я родом оттуда? Но тогда получается, что оно уже уничтожено?"
    "Всё плыло в моей голове. Практически превозмогая себя, я старался держаться на ногах и не терять чувство реальности"
    shtrauf "Ред, [me], я думаю, вам стоит идти. Вы и так видели слишком много. Боюсь, как бы вы не попали в такую передрягу, откуда уже не сможете уйти живыми. Это недопустимо"
    hide Shtrauf with dissolve
    "Генерал направился к двери, чтобы открыть её и проводить нас из дворца. Но как только рука его коснулась её, что-то громкое упало на пол позади нас всех"
    me "Сэр Штрауф, берегитесь!"
    image frozen_monster = "images/frozen_monster.png"
    show frozen_monster with fade
    "Огромный, неизвестной ранее формы, монтр прыгнул в сторону Штрауфа, разнеся в одно мгновение несколько мраморных колонн!"
    "Это существо нельзя было описать словами - неведомый мутант, источавший ледяной холод и ужас прямо вокруг себя оказался так внезапно в метре от нас!"
    "сэр Штрауф, не успевший ворвемя среагировать, отлетел к противоположной стене, оставив меня с Редом одних против этого немыслимого создания"
    shtrauf "Бегите! Бегите, пока не поздно! Предупредите армию, что во дворце враг!!!"
    me "Ред, быстрее беги к страже. Мы со Штрауфом попытаемся задержать это существо, но с его силой долго мы не продержимся! Поторопись!"
    "Ред кинулся к двери из зала, а я же встал между ним и монстром наготове, стараясь как можно крепче держать свой новый серебряный меч"
    shtrauf "Что ты чёрт возьми делаешь?! Беги, пока это существо тебя не прикончило!"
    me "Сэр Штрауф, я не собираюсь бежать. Лучше помогите мне уничтожить его до того, как оно выберется наружу. Я видел вашу атаку в битве с Ваалом, сколько времени нужно, чтобы подготовить её?"
    shtrauf "Минут пять... Если ты сможешь его задержать хотя бы на это время, я смогу использовать Разрушитель Небес... Но  на это время ответственность за выживание будет лежать только на тебе..."
    me "Я справлюсь! Готовьтесь атаковать его!"
    "Это всего лишь очередной монстр... Всего лишь ещё один враг, которого нужно одолеть, просто чуть более сильный. Я справлюсь, на моей стороне генерал армии Луфтена!"
    $ renpy.block_rollback()

    define frozen_monster = None

    $ attacks = []
    $ attacks.append(attack("Ледяное Порождение окружает зал льдом!", std_base_attack, 80, 0)) #base
    $ attacks.append(attack("Ледяное Порождение выпускает в вас шипы!", std_base_attack, 90, 0)) #base
    $ attacks.append(attack("Ледяное Порождение прыгает в вашу сторону!", std_base_attack, 100, 0)) #base

    $ frozen_monster = enemy("Ледяное Порождение", 50000, std_enemy_update, std_enemy_rand, "i")
    $ frozen_monster.attacks = attacks

    $ Player = player(level, xp, std_player_update)
    $ Player.attacks.append(attack("Молниеносный удар", lightning_attack, value = Player.max_damage, cost = 2))
    $ Player.attacks.append(attack("Смертельный вихрь", tornado_attack, value = Player.max_damage, cost = 2))

    $ Log = log(wait10turns_check, std_lose_check, std_log_update, "Начался бой с Ледяным Порождением!")

    call screen fight_screen(Log, Player, frozen_monster)

    $ newLv = Player.add_xp(800) # 3600 / 4500
    $ level = Player.level
    $ xp += 800

    $ renpy.block_rollback()
    hide frozen_monster with fade

    "Вы получаете 800 ед. опыта!"
    if newLv:
        "Ваш уровень повышен до [level]!"

    "Еле успев отпрыгнуть, я падаю на мраморный, полный трещин пол, прикрывая рукой своё лицо от обжигающих лучей атаки Штрауфа. Всё вокруг заполнено огнём, всё вокруг горит красным пламенем!"
    "постаравшись привстать, я понимаю, что силы мои почти на исходе. Ещё бы чуть-чуть, и вряд ли бы сейчас я был вживых. Однако, всё обошлось..."
    show Shtrauf with dissolve
    show guardian_left at left with moveinleft
    show guardian_right at right with moveinright
    "Вбежавшая стража помогла мне подняться с пола и отряхнула меня от пепла. Немного хромая, я подобрал свой меч и пошёл посмотреть на тот труп, который поразила атака генерала"
    me "Да уж, он точно мёртв после такого удара... Что же это было за существо, сэр Штрауф?"
    shtrauf "Это был ответный удар на нашу попытку узнать происхождение того кабана... Видимо, враг уже знает, что мы пытаемся найти его, и где мы находимся... Это очень плохо"
    "Сэр Штрауф перевязал себе повреждённую левую руку и направился к выходу из полуразрушенного дворцового зала, немного хромая на одну из ног. Видимо сильно ему досталось в тот момент..."
    scene bg luften_gates with dissolve
    show Shtrauf
    "Мы наконец-то вышли за пределы королевского собора и снова оказались перед главными воротами. Теперь повсюду бегала стража, кто-то относил раненых в палаты, кто-то восстанавливал разрушенный фасад"
    shtrauf "Это большой просчёт, что такой сильный враг смог пробраться внутрь дворца. Даже поверить не могу, что такое могло произойти в самый обычный день! Куда они все смотрели?"
    "Генерал от злости ударил кулаком по стене замка. Ред тем временем помогал мне залечивать нанесённые в бою раны, что-то про себя приговаривая"
    me "Господин Штрауф, а вам не кажется, что монстр не смог бы пробраться внутрь... Что если, он был призван внутри? Кем-то, кто уже находился во дворце в тот момент, когда мы разговаривали в зале?"
    shtrauf "Я обдумывал этот вариант. Такое не исключено, и уж больно похоже на правду. Но в данный момент тяжело даже назвать имена подозреваемых, очень большое число людей знало о вашем визите"
    shtrauf "Но то место, что мы видели в иллюзии печати, явно даёт нам наводку, где можно искать следы врага. Я бы не советовал вам отправляться туда, но и препятствовать вам не могу"
    shtrauf "И да, [me], большое тебе спасибо. Ты хорошо продержался против этой твари, без твоей помощи скорее всего меня бы просто прикончили. Ты правда большой молодец, поздравляю"
    "Штрауф протянул мне правую руку и я с гордостью пожал её. Пожелав удачи генералу, мы наконец смогли покинуть дворец, отправившись обратно в центр Луфтена. Однако, место это для меня уже не было прежним..."
    scene bg luften1 with dissolve
    "Может враг не знает наших имён, а мы его, но то, что мы все находимся в Луфтене, известно уже каждому нашему врагу. И этот факт никогда не даст мне спокойно уснуть, никогда не даст мне покоя..."
