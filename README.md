# Embedded QA in IoT & DefTech — Testing Portfolio

**Author:** Denys Obertovych (Обертович Денис)  
**Repository:** [github.com/OberDen/EmbededQA](https://github.com/OberDen/EmbededQA)  
**Role:** Embedded QA Engineer  
**Target Platforms:** ESP32 DevKit v1, Arduino Uno (Wokwi Simulation & HIL-ready)  

---

## 📌 1. Project Overview & System Scope

Цей репозиторій містить повний цикл артефактів контролю якості вбудованого програмного забезпечення (Embedded QA) для модульної IoT / DefTech системи керування виконавчими механізмами та збору телеметрії. Тестування охоплює рівні від низькорівневих апаратних переривань і цифрових шин даних до мережевої стабільності та автоматизації на Python/Pytest.

### System Under Test (SUT) Scope
* **Hardware & Peripherals:**
  * **MCUs:** ESP32 DevKit v1 (основний контролер телеметрії, CLI, WDT, NVS та мережевого стека), Arduino Uno (Smart Gate FSM контролер).
  * **Sensors:** `MPU6050` (I2C адреса `0x68`, SDA: GPIO21, SCL: GPIO22), `DHT22` (GPIO15).
  * **Inputs & Fault Triggers:** Кнопки керування з генераторами контактного брязкоту та імпульсного шуму (GPIO18, GPIO4), кінцеві вимикачі `LIMIT_OPEN` / `LIMIT_CLOSE`, тумблер ін'єкції апаратних збоїв шини `FAULT`.
  * **Actuators & Indicators:** Силові реле (`OPEN relay`, `CLOSE relay`, `Relay GPIO5`), ШІМ-виходи (`PWM 0..100`), світлодіодна індикація станів (`GPIO2`, Green/Red/Yellow LEDs), звуковий зумер (`Buzzer`).
* **Firmware Subsystems Tested:**
  * **W1 — Smart Gate FSM:** Машина станів (`CLOSED`, `OPENING`, `OPEN`, `CLOSING`, `STOPPED`, `ERROR`), взаємоблокування реле та таймаути руху (>10 с).
  * **W2 — GPIO, Interrupts & Debounce:** Обробники переривань (ISR), фільтрація брязкоту контактів та захист від високочастотних імпульсних завад під час критичних операцій.
  * **W3 — UART / Serial CLI:** Парсер текстових команд (115200 baud), валідація границь параметрів (`SPEED 0..255`, `TIMEOUT 1..60`), керування станами конфігурації (`SAVED` / `DIRTY`).
  * **W4 — I2C Protocol & Bus Faults:** Низькорівневий обмін із датчиком `MPU6050`, аналіз транзакцій `ACK/NACK`, перевірка таймаутів та відновлення після втрати периферії.
  * **W5 — Recovery, WDT, Sleep & Persistence:** Сторожовий таймер (`Task WDT`, 4000 мс), енергоощадний режим `Deep Sleep`, атомарність збереження даних у NVS/Flash при раптовому зникненні живлення (`powerloss`).
  * **W6 — Python / Pytest Host Automation:** Автоматизоване тестування JSON CLI протоколу через міст `rfc2217://localhost:4000`.
  * **W7 — IoT Network & Memory Stability:** Керування станами мережі (`CONNECTED`, `DISCONNECTED`, `BACKOFF`, `CONNECTING`), офлайн-буфер телеметрії (8 слотів, `DROP_OLDEST`), дедуплікація MQTT-пакетів та профілювання витоків пам'яті (`free heap`).

---

## 📂 2. Repository Structure & Evidence Package

```text
EmbededQA/
├── MASTER_TEST_PLAN.md                                      # Повний Master Test Plan проєкту
├── README.md                                                # Огляд портфоліо, інструкції та висновки
├── docs/
│   ├── Hardware_Test_Sheet_Test_Log_Obertovych.docx         # W1: Smart Gate FSM (24 TC, 4 Bugs)
│   ├── Debounce_Test_Sheet_Test_Log_Obertovych_UPDATED.docx # W2: GPIO / ISR / Debounce (7 TC, 2 Bugs)
│   ├── UART_CLI_Test_Sheet_Test_Log_Webinar_3_UPDATED.docx  # W3: UART CLI & Parser (29 TC, 6 Bugs)
│   ├── Protocol_Analysis_Sheet_Test_Log_Webinar_4.docx      # W4: I2C Bus & Logic Analyzer (1 Critical Bug)
│   ├── Recovery_Fault_Injection_Test_Sheet_Webinar_5.docx   # W5: WDT, Deep Sleep, NVS (7 Scenarios, 5 Bugs)
│   ├── Python_Pytest_Test_Sheet_Webinar_6_UPDATED.docx      # W6: Pytest CLI Triage (21 Auto-tests, 4 Bugs)
│   ├── IoT_Network_Memory_Test_Sheet_Webinar_7_UPDATED.docx # W7: MQTT Buffer & Heap Stability (4 Bugs)
│   └── Portfolio_Review_Sheet_Webinar_8.docx                # W8: Чек-лист фінального оцінювання
├── evidence/
│   ├── traces/
│   │   └── wokwi.vcd                                        # Дамп сигналів SDA/SCL для PulseView (I2C NACK)
│   ├── media/
│   │   ├── WDT.gif                                          # Доказ спрацювання Task WDT (< 5 s)
│   │   └── Sleep_5.gif                                      # Доказ передчасного пробудження з Deep Sleep (0.5 s)
│   └── logs/                                                # Сирі UART логи, скріншоти консолей та PulseView
└── pytest/
    └── automation/
        ├── pytest.ini                                       # Конфігурація тестового фреймворку
        ├── device.py                                        # Клієнт обміну з МК через PySerial / RFC2217
        └── tests/
            └── test_firmware_cli.py                         # Набір із 21 автотесту для перевірки прошивки
```

---

## ⚠️ 3. Key Quality Risks (5+ Core Risks)

| Risk ID | Категорія ризику | Опис ризику та потенційний наслідок | Пріоритет | Покриття в тестах |
|---|---|---|---|---|
| **RISK-01** | **Actuator Safety Hazard** | Залипання силових реле або ШІМ у стані `ON` після досягнення кінцевих вимикачів, таймауту руху (>10 с), команди `RESET` або аварійного перезавантаження через WDT. Загрожує фізичним пошкодженням механізму. | **P0 (Blocker)** | W1 (`TC-03`, `TC-12..15`), W5 (`Relay + WDT`), W6 (`T-05`) |
| **RISK-02** | **ISR Noise & False Triggers** | Відсутність фільтрації коротких електричних наводок на GPIO, що викликає несанкціоноване спрацьовування виконавчих механізмів у стані спокою або під час критичної операції. | **P1 (Critical)** | W2 (`TC-06`, `TC-07`), W5 (`Button`) |
| **RISK-03** | **CLI Buffer Overflow & Crash** | Переповнення вхідного буфера UART (>40 символів) або неконсистентність стану парсера при незбереженій конфігурації (`CONFIG=DIRTY`), що призводить до `SYSTEM FAULT` та перезавантаження МК (`SW_CPU_RESET`). | **P1 (Critical)** | W3 (`TC-20..23`), W6 (`T-03`) |
| **RISK-04** | **Bus Hang & Deadlock** | Відсутність таймаутів та механізму retry при втраті зв'язку з периферією по шині I2C (`NACK`), що назавжди блокує виконання `main loop` навіть після фізичного відновлення датчика. | **P0 (Blocker)** | W4 (`Fault Timeline`, `.vcd` trace) |
| **RISK-05** | **NVS Data Corruption** | Порушення атомарності запису у флеш-пам'ять при раптовому зникненні живлення (`powerloss during save`), що породжує змішаний/пошкоджений стан (`counter: 101`) без його виявлення при старті. | **P1 (Critical)** | W5 (`Interrupted save`) |
| **RISK-06** | **Memory Leak (Heap Exhaustion)** | Систематичне незворотне зменшення вільної оперативної пам'яті (`free heap`) під час передачі телеметрії (~80 байт на пакет), що веде до гарантованого крешу ноди під час тривалої експлуатації. | **P0 (Blocker)** | W7 (`STRESS 100` x 10 ітерацій) |
| **RISK-07** | **Reconnect Storm & Telemetry Loss/Duplication** | Аномально малий інтервал повторних підключень (50 мс замість експоненційного backoff), ігнорування ліміту офлайн-буфера (8 повідомлень) та багаторазове дублювання пакетів після відновлення мережі. | **P2 (Major)** | W7 (`NET DOWN/UP`, `Offline buffer`, `Boundary capacity`) |

---

## 📊 4. Master Test Matrix & Execution Summary

Загалом у межах проєкту виконано **96+ перевірок** (ручних сценаріїв, аналізів протоколів, ін'єкцій збоїв та автоматизованих тестів), за результатами яких задокументовано **26 дефектів**.

| Модуль / Вебінар | Об'єкт тестування | Всього тестів | Passed | Failed | Знайдено багів | Ключові інструменти та методи |
|---|---|---:|---:|---:|---:|---|
| **W1: Smart Gate Controller** | FSM, Relays, Limit Switches, Timeouts | 24 | 20 | 4 | **4** (`2 Critical`, `2 Med`) | Wokwi, Arduino Uno, State Transition, Black-box |
| **W2: GPIO & Debounce** | GPIO18 ISR, Contact Bounce, Noise Injection | 7 | 5 | 2 | **2** (`2 High`) | ESP32, Wokwi Noise Generator, Interrupt Logging |
| **W3: UART / CLI** | CLI Parser, Boundaries, `SAVED/DIRTY` States | 29 | 23 | 6 | **6** (`5 High`, `1 Major`) | Serial Monitor (115200), BVA, Equivalence Partitioning |
| **W4: I2C Protocol** | `MPU6050` (`0x68`), `SDA/SCL`, `ACK/NACK` Recovery | 3 фази | 1 | 2 | **1** (`1 Critical`) | Logic Analyzer (`.vcd`), **PulseView**, Grey-box |
| **W5: Recovery & Faults** | Deep Sleep, Task WDT, Power Loss, `DHT22` | 7 | 2 | 5 | **5** (`2 Crit`, `2 High`, `1 Maj`) | Fault Injection (`hang`, `powerloss`), Reset Reason Analysis |
| **W6: Pytest Automation** | JSON CLI API, `PING`, `GET TEMP`, `PWM 0..100` | 21 | 17 | 4 | **4** (`1 Crit`, `1 High`, `2 Maj`) | **Python 3.15.2**, **Pytest 9.2.0**, `pyserial`, `rfc2217` |
| **W7: IoT Network & Heap** | MQTT Reconnect, Offline Buffer (8), Heap Stress | 5 блоків | 1 | 4 | **4** (`1 Crit`, `3 Major`) | Network State Model, `STRESS 100` Heap Profiling |
| **РАЗОМ** | **Комплексна система IoT / DefTech** | **96** | **69** | **27** | **26 дефектів** | **Black-box, Grey-box, Protocol Analysis, Automation** |

---

## 🐞 5. Highlighted Critical Bug Reports (Top Findings)

Детальні звіти з повними логами та скріншотами містяться у відповідних документах у папці `docs/` та у зведеній таблиці [MASTER_TEST_PLAN.md](./MASTER_TEST_PLAN.md). Нижче наведено 5 найкритичніших знахідок:

1. **`[BUG-W4-01]` (Critical) — Повне зависання Main Loop при втраті I2C-периферії (`NACK`):**
   * **Опис:** Після активації тумблера `FAULT ON` на шині I2C фіксується `NACK` на записі адреси `0x69` (таймштамп `+5.519494 s`), а у консоль виводиться `[Wire.cpp:499] requestFrom(): i2cWriteReadNonStop returned Error -1`. Прошивка не має механізму retry/timeout і блокує основний цикл назавжди — навіть після повернення перемикача у `FAULT OFF` робота не відновлюється без повного апаратного перезапуску.
2. **`[BUG-W7-04]` (Critical) — Лінійний витік оперативної пам'яті (`Memory Leak`) під час передачі телеметрії:**
   * **Опис:** При виконанні 10 серій навантаження `STRESS 100` (1000 MQTT-повідомлень) обсяг вільного купа (`free heap`) монотонно та незворотно падає з `350 868` байт до `270 600` байт. Втрата становить **80 268 байт (~22.9% RAM)**, або рівно `80 байт` на кожне повідомлення.
3. **`[BUG-W5-02]` & `[BUG-W6-T05]` (Critical) — Порушення безпечного стану виконавчих механізмів після WDT Reset та команди `RESET`:**
   * **Опис:** Якщо реле було увімкнене (`relay on`) до зависання системи (`hang`), після спрацювання сторожового таймера (`rst:0x8 TG1WDT_SYS_RESET`) реле залишається у небезпечному стані `"relay":true` замість аварійного вимкнення. Аналогічно в автотесті `test_reset_restores_safe_state` команда `RESET` не скидає виходи, залишаючи `"led":true` та встановлюючи `"pwm":255` замість `0`.
4. **`[BUG-W3-22]` & `[BUG-W3-23]` (High/Critical) — Аварійне перезавантаження МК (`SYSTEM FAULT`) через парсер CLI:**
   * **Опис:** Введення рядка довжиною 41 символ (при ліміті 40) або введення неповної команди `set` у стані незбереженої конфігурації (`CONFIG=DIRTY`) призводить до крашу прошивки (`Reason: input line boundary failure` / `parser state mismatch`) та програмного скидання процесора `rst:0xc (SW_CPU_RESET)`.
5. **`[BUG-W5-03]` (High) — Порушення атомарності NVS при зникненні живлення (`Interrupted Save`):**
   * **Опис:** Імітація втрати живлення під час збереження конфігурації (`[FAULT] power loss DURING save`) призводить до часткового запису: після перезавантаження лічильник станів має невалідне значення `"counter":101` (замість попереднього `0` або нового `1`), при цьому прошивка не розпізнає пошкодження структури даних.

---

## 🤖 6. Test Automation (Python + Pytest)

Автоматизований тестовий набір перевіряє роботу JSON CLI через послідовний порт (або мережевий міст `RFC2217` із симулятора Wokwi).

### Вимоги до оточення
* **Python:** `3.15.2` (або `3.10+`)
* **Packages:** `pytest==9.2.0`, `pyserial==3.5`
* **Port Configuration:** `DEVICE_PORT = rfc2217://localhost:4000` (Baudrate: `115200`)

### Запуск автотестів
```powershell
# 1. Перехід у директорію автотестів
cd .\pytest\automation

# 2. Створення та активація віртуального середовища
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. Встановлення залежностей
pip install pytest pyserial

# 4. Запуск тестового набору з детальним звітом
python -m pytest -v .\tests\test_firmware_cli.py
```

### Результати останнього прогону (Triage Summary)
* **Загальний результат:** `4 failed, 17 passed in 43.91s`
* **Виявлені падіння:**
  * `FAILED test_ping` — `TimeoutError: No response for command: PING` *(Clasification: Requirement / Protocol mismatch)*
  * `FAILED test_temperature_is_valid_json` — `AssertionError: Invalid JSON from device: '{"status":"OK","temperature":24.5'` *(Classification: Firmware Defect — обірваний JSON)*
  * `FAILED test_reset_restores_safe_state` — `AssertionError: assert 255 == 0` *(Classification: Critical Firmware Safety Defect)*
  * `FAILED test_pwm_valid_boundaries[100]` — `AssertionError: assert 'ERROR' == 'OK'` *(Classification: Firmware Boundary Defect — значення 100 відхиляється)*

---

## 🛑 7. Release Decision & QA Conclusion

### **Фінальне рішення щодо релізу: ❌ NO-GO (Реліз заблоковано)**

### QA Conclusion (Підсумковий висновок)
Проведене комплексне тестування показало, що хоча базові позитивні сценарії (*Happy Path*) виконуються коректно на всіх підсистемах, **прошивка не відповідає критичним вимогам надійності, безпеки та відмовостійкості (Robustness & Safety)**, необхідним для експлуатації в IoT та DefTech середовищі:

1. **Критичні ризики безпеки (Safety Blockers):** Приводи та виконавчі механізми не захищені при збоях. Відсутність зупинки за кінцевиком `LIMIT_OPEN`, ігнорування таймауту відкриття (>10 с), збереження увімкненого стану реле після спрацювання WDT та встановлення `PWM=255` після команди `RESET` створюють пряму загрозу аварії обладнання.
2. **Критичні проблеми стабільності та доступності (Availability Blockers):**
   * Відсутність обробки помилок шини I2C (`NACK`) призводить до повного зависання пристрою при тимчасовому збої датчика.
   * Наявність стабільного витоку пам'яті (`80 байт/повідомлення`) унеможливлює тривалу автономну роботу ноди.
   * Вразливості парсера CLI дозволяють викликати аварійне перезавантаження контролера через переповнення буфера рядка (41 символ) або неповну команду.
3. **Необхідні кроки для досягнення статусу GO:**
   * Усунути всі дефекти рівнів **Critical (7 шт.)** та **High (11 шт.)**.
   * Реалізувати гарантоване скидання всіх GPIO/Relay/PWM у безпечний стан (`OFF`/`0`) на етапі ініціалізації після будь-якого типу перезавантаження та аварії.
   * Додати таймаути та логіку повторних спроб (retry) для драйвера I2C і експоненційний backoff для мережевого стека.
   * Виправити звільнення динамічної пам'яті при публікації MQTT-повідомлень та забезпечити атомарність транзакцій NVS (через CRC/подвійну буферизацію).
   * Успішно пройти повний регресійний прогін Pytest (`21/21 Pass`) та провести фінальну верифікацію живлення (*brown-out*) на фізичному стенді ESP32.