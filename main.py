#nastavení základních parametrů
speedFactor = 50
pin_L = DigitalPin.P15
pin_R = DigitalPin.P14
pin_M = DigitalPin.P13
pin_Trig = DigitalPin.P1
pin_Echo = DigitalPin.P8
whiteline = 0
connected = 0
pins.set_pull(pin_L, PinPullMode.PULL_NONE)
pins.set_pull(pin_R, PinPullMode.PULL_NONE)
pins.set_pull(pin_M, PinPullMode.PULL_NONE)
bluetooth.start_uart_service()
uartData = ""
where = "forward"
manual = False
line_follower = True
speed = 255
around = False

# Funkce na zlehčení použití motorů
def motor_run(left = 0, right = 0):
    PCAmotor.motor_run(PCAmotor.Motors.M1, Math.map(Math.constrain(left * (speedFactor / 100), -100, 100), -100, 100, -255, 255))
    PCAmotor.motor_run(PCAmotor.Motors.M4, Math.map(Math.constrain(-1 * right * (speedFactor / 100), -100, 100), -100, 100, -255, 255))

# Funkce pro připojení mobilního zařízení + sbírání dat
def on_bluetooth_connected():
    global connected, uartData
    basic.show_icon(IconNames.HEART)
    connected = 1
    while connected == 1:
        uartData = bluetooth.uart_read_until(serial.delimiters(Delimiters.HASH)) # sbírat data
bluetooth.on_bluetooth_connected(on_bluetooth_connected)
#funkce pro odpojení mobilního zařízení
def on_bluetooth_disconnected():
    global connected
    basic.show_icon(IconNames.SAD)
    connected = 0
bluetooth.on_bluetooth_disconnected(on_bluetooth_disconnected)

def on_forever():
    global uartData , where, manual, line_follower , speed, around
    obstacle_distance = sonar.ping(pin_Trig, pin_Echo, PingUnit.CENTIMETERS, 100)   #sbíraní dat ze sonaru
    l = False if (whiteline ^ pins.digital_read_pin(pin_L)) == 0 else True #sbíraní dat z levého senzoru
    r = False if (whiteline ^ pins.digital_read_pin(pin_R)) == 0 else True #sbíraní dat z pravého senzoru
    m = False if (whiteline ^ pins.digital_read_pin(pin_M)) == 0 else True #sbíraní dat z prostředního senzoru

    if uartData == "E": # na další křížovatce doleva
        where = "left"
    elif uartData == "F": # na další křížovatce doprava
        where = "right"
    elif uartData == "U": # přepnout na manualní řízení
        PCAmotor.motor_stop_all()
        manual = True
        line_follower = False
    elif uartData == "V": # přepnout na jízdu po čáře
        PCAmotor.motor_stop_all()
        manual = False
        line_follower = True
    elif uartData == "A": # přidat rychlost
        if speed != 255:
            speed += 50
    elif uartData == "B": # odebrat rychlost
        if speed != 105:
            speed -= 50
    elif uartData == "C": # objet objekt
        around = True

    if manual:
        control.in_background(manual_wsad)

    # if line_follower:   #jízda na 2 senzory (doma mám úzkou pásku, takže to bylo nemožné jet optimálně na 3)
    #     if obstacle_distance <=15 and obstacle_distance !=0: # když sonar zaznamená méně než 15 cm
    #         if not around: # => otoč se
    #             motor_run(255, -255);basic.pause(400)
    #         else:   # => objet objekt 20x20x20 ...
    #             motor_run(255, -255);basic.pause(200)   #doleva
    #             motor_run(-255, -255);basic.pause(750)  #rovně
    #             motor_run(-255, 255);basic.pause(200)   #doprava
    #             motor_run(-255, -255);basic.pause(1500)  #rovně
    #             motor_run(-255, 255);basic.pause(200)   #doprava
    #             motor_run(-255, -255);basic.pause(750)  #rovně
    #             motor_run(255, -255);basic.pause(200)   #doleva
    #         around = False

    #     elif  r and  l: # když zaznamená pravý i levý senzor (počítáno s tím že je to křižovatka) =>
    #         if where == "left": # zaboč doleva
    #             motor_run(-255, -255);basic.pause(75)
    #             motor_run(255, -255);basic.pause(200)
    #             PCAmotor.motor_stop_all();basic.pause(150)
    #         elif where == "right": # zaboč doprava
    #             motor_run(-255, -255);basic.pause(75)
    #             motor_run(-255, 255);basic.pause(200)
    #             PCAmotor.motor_stop_all();basic.pause(150)
    #         elif where == "forward": # neodbočuj
    #             motor_run(-255 , -255)
    #         where = "forward" # po přejetí křižovatky nastav se defaulně do projetí křižovatkou rovně

    #     elif not r and not l: # když nesnímáš čáru => rovně
    #         motor_run( -1* speed, -1* speed)
    #     elif l: # když levý senzor snímá čáru => zaboč doleva
    #         motor_run(-60, 60)
    #     elif r: # když pravý senzor snímá čáru => zaboč doprava
    #         motor_run(60, -60)



    if line_follower:   #jízda na 3 senzory
       if obstacle_distance <=15 and obstacle_distance !=0: # když sonar zaznamená méně než 15 cm
           if not around: # => otoč se
               motor_run(255, -255);basic.pause(400)
           else:   # => objet objekt 20x20x20 ...
               motor_run(255, -255);basic.pause(200)   #doleva
               motor_run(-255, -255);basic.pause(750)  #rovně
               motor_run(-255, 255);basic.pause(200)   #doprava
               motor_run(-255, -255);basic.pause(1500)  #rovně
               motor_run(-255, 255);basic.pause(200)   #doprava
               motor_run(-255, -255);basic.pause(750)  #rovně
               motor_run(255, -255);basic.pause(200)   #doleva
           around = False
       elif not m and not l and not r: #kduž ani jeden ze senzorů nesnímá čáru => couvej
               motor_run(255, 255)
       elif  r and  l and m: # když zaznamená pravý, prostřední i levý senzor (počítáno s tím že je to křižovatka) =>
           if where == "left": # zaboč doleva
               motor_run(-255, -255);basic.pause(75)
               motor_run(255, -255);basic.pause(200)
               PCAmotor.motor_stop_all();basic.pause(150)
           elif where == "right": # zaboč doprava
               motor_run(-255, -255);basic.pause(75)
               motor_run(-255, 255);basic.pause(200)
               PCAmotor.motor_stop_all();basic.pause(150)
           elif where == "forward": # neodbočuj
               motor_run(-255 , -255)
           where = "forward" # po přejetí křižovatky nastav se defaulně do projetí křižovatkou rovně

       elif not r and not l and m: # když nesnímáš čáru => rovně
           motor_run(-255, -255)
       elif l and m: # když levý a prostřední senzor snímá čáru => zaboč doleva
           motor_run(-60, 60)
       elif r and m: # když pravý a prostřední senzor snímá čáru => zaboč doprava
           motor_run(60, -60)

basic.forever(on_forever)


# FUNKCE pro ovládíní mobilním zařízením
def manual_wsad():
    global uartData
    if uartData == "E": #mírně doleva
        motor_run(-100, -255)
    elif uartData == "F": #mírně doprava
        motor_run(-255, -100)
    elif uartData == "A":   #dopředu
        motor_run(-255, -255)
    elif uartData == "B":   #dozadu
        motor_run(255, 255)
    elif uartData == "C":   #otočit doprava
        motor_run(255, -255)
    elif uartData == "D":   #otočit doleva
        motor_run(-255, 255)
    elif uartData == "0":   #když bylo tlačítko "odmáčknuto" zastav se
        PCAmotor.motor_stop_all()