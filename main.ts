// nastavení základních parametrů
let speedFactor = 50
let pin_M = DigitalPin.P15
let pin_R = DigitalPin.P14
let pin_L = DigitalPin.P13
let pin_Trig = DigitalPin.P2
let pin_Echo = DigitalPin.P1
let whiteline = 0
let connected = 0
pins.setPull(pin_L, PinPullMode.PullNone)
pins.setPull(pin_R, PinPullMode.PullNone)
pins.setPull(pin_M, PinPullMode.PullNone)
bluetooth.startUartService()
let uartData = ""
let where = "forward"
let manual = false
let line_follower = true
let speed = 160
let around = false
//  Funkce na zlehčení použití motorů
function motor_run(left: number = 0, right: number = 0) {
    PCAmotor.MotorRun(PCAmotor.Motors.M1, Math.map(Math.constrain(-1* left * (speedFactor / 100), -100, 100), -100, 100, -199, 199))
    PCAmotor.MotorRun(PCAmotor.Motors.M4, Math.map(Math.constrain(-1 * right * (speedFactor / 100), -100, 100), -100, 100, -130, 130))
}

//  Funkce pro připojení mobilního zařízení + sbírání dat
//  sbírat data
bluetooth.onBluetoothConnected(function on_bluetooth_connected() {
    
    basic.showIcon(IconNames.Duck)
    connected = 1
    while (connected == 1) {
    }
})
// funkce pro odpojení mobilního zařízení
bluetooth.onBluetoothDisconnected(function on_bluetooth_disconnected() {
    
    basic.showIcon(IconNames.Sad)
    connected = 0
})
basic.forever(function on_forever() {
    
    let obstacle_distance = sonar.ping(pin_Trig, pin_Echo, PingUnit.Centimeters, 100)
    // sbíraní dat ze sonaru
    let l = (whiteline ^ pins.digitalReadPin(pin_L)) == 0 ? false : true
    // sbíraní dat z levého senzoru
    let r = (whiteline ^ pins.digitalReadPin(pin_R)) == 0 ? false : true
    // sbíraní dat z pravého senzoru
    let m = (whiteline ^ pins.digitalReadPin(pin_M)) == 0 ? false : true
    // sbíraní dat z prostředního senzoru
    if (uartData == "E") {
        //  na další křížovatce doleva
        where = "left"
    } else if (uartData == "F") {
        //  na další křížovatce doprava
        where = "right"
    } else if (uartData == "U") {
        //  přepnout na manualní řízení
        PCAmotor.MotorStopAll()
        manual = true
        line_follower = false
    } else if (uartData == "V") {
        //  přepnout na jízdu po čáře
        PCAmotor.MotorStopAll()
        manual = false
        line_follower = true
    } else if (uartData == "A") {
        //  přidat rychlost
        if (speed != 255) {
            speed += 50
        }
        
    } else if (uartData == "B") {
        //  odebrat rychlost
        if (speed != 105) {
            speed -= 50
        }
        
    } else if (uartData == "C") {
        //  objet objekt
        around = true
    }
    
    // if (manual) {
    //     control.inBackground(function manual_wsad() {
            
    //         if (uartData == "E") {
    //             // mírně doleva
    //             motor_run(-100, -255)
    //         } else if (uartData == "F") {
    //             // mírně doprava
    //             motor_run(-255, -100)
    //         } else if (uartData == "A") {
    //             // dopředu
    //             motor_run(-255, -255)
    //         } else if (uartData == "B") {
    //             // dozadu
    //             motor_run(255, 255)
    //         } else if (uartData == "C") {
    //             // otočit doprava
    //             motor_run(255, -255)
    //         } else if (uartData == "D") {
    //             // otočit doleva
    //             motor_run(-255, 255)
    //         } else if (uartData == "0") {
    //             // když bylo tlačítko "odmáčknuto" zastav se
    //             PCAmotor.MotorStopAll()
    //         }
            
    //     })
    // }

    if (line_follower) {
        // jízda na 3 senzory
        if (obstacle_distance <= 15 && obstacle_distance != 0) {
            //  když sonar zaznamená méně než 15 cm
            if (!around) {
                //  => otoč se
                motor_run(160, -160)
                basic.pause(400)
            } else {
                //  => objet objekt 20x20x20 ...
                motor_run(-160, 160)
                basic.pause(100)
                // doprava
                motor_run(-160, -160)
                basic.pause(380)
                // rovně
                motor_run(160, -160)
                basic.pause(100)
                // doleva
                motor_run(-160, -160)
                basic.pause(750)
                // rovně
                motor_run(160, -160)
                basic.pause(100)
                // doleva
                motor_run(-160, -160)
                basic.pause(380)
                // rovně
                motor_run(160, -160)
                basic.pause(100)
            }
            
            // doleva
            around = false
        } else if (!m && !l && !r) {
            // kduž ani jeden ze senzorů nesnímá čáru => couvej
            motor_run(160, 160)
        } else if (r && l && m) {
            //  když zaznamená pravý, prostřední i levý senzor (počítáno s tím že je to křižovatka) =>
            if (where == "left") {
                //  zaboč doleva
                motor_run(-160, -160)
                basic.pause(75)
                motor_run(160, -160)
                basic.pause(200)
                PCAmotor.MotorStopAll()
                basic.pause(150)
            } else if (where == "right") {
                //  zaboč doprava
                motor_run(-160, -160)
                basic.pause(75)
                motor_run(-160, 160)
                basic.pause(200)
                PCAmotor.MotorStopAll()
                basic.pause(150)
            } else if (where == "forward") {
                //  neodbočuj
                motor_run(-160, -160)
            }
            
            where = "forward"
        } else if (!r && !l && m) {
            //  po přejetí křižovatky nastav se defaulně do projetí křižovatkou rovně
            //  když nesnímáš čáru => rovně
            motor_run(199, 130)
        } else if (l && m) {
            //  když levý a prostřední senzor snímá čáru => zaboč doleva
            motor_run(100, -100)
        } else if (r && m) {
            //  když pravý a prostřední senzor snímá čáru => zaboč doprava
            motor_run(-100, 100)
        }
        
    }
    
})