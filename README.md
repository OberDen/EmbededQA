# Embedded QA in IoT & DefTech — Testing Portfolio

**Author:** Denys Obertovych (Обертович Денис)  
**Repository:** [github.com/OberDen/EmbededQA](https://github.com/OberDen/EmbededQA)  
**Role:** Embedded QA Engineer  
**Target Platforms:** ESP32 DevKit v1, Arduino Uno (Wokwi Simulation)

---

## 📌 1. Project Overview & System Scope

Цей репозиторій містить повний цикл артефактів контролю якості вбудованого програмного забезпечення (Embedded QA) для навчально-тестових модулів IoT / DefTech системи керування виконавчими механізмами та збору телеметрії. Тестування охоплює **7 підсистем (W1–W7)**: від низькорівневих апаратних переривань і цифрових шин даних до програмної моделі мережевого стека, стабільності оперативної пам'яті та автоматизації на Python/Pytest.

### System Under Test (SUT) Scope

* **Simulated Hardware & Peripherals (Wokwi):**
  * **MCUs:** ESP32 DevKit v1 (модулі W2–W7: контролер телеметрії, CLI, WDT, NVS та моделі мережі), Arduino Uno (модуль W1: Smart Gate FSM контролер).
  * **Sensors:** `MPU6050` (I2C адреса `0x68`, SDA: GPIO21, SCL: GPIO22), `DHT22` (GPIO15).
  * **Inputs & Fault Triggers:** Кнопки керування з генераторами контактного брязкоту та імпульсного шуму (GPIO18, GPIO4), кінцеві вимикачі `LIMIT_OPEN` / `LIMIT_CLOSE`, віртуальний тумблер ін'єкції збоїв шини `FAULT`.
  * **Actuators & Indicators:** Силові реле (`OPEN relay`, `CLOSE relay`, `Relay GPIO5`), ШІМ-виходи (`PWM 0..100`), світлодіодна індикація станів (`GPIO2`, Green/Red/Yellow LEDs), звуковий зумер (`Buzzer`).

* **Firmware Subsystems Tested (7 Modules):**
  * **W1 — Smart Gate FSM:** Машина станів (`CLOSED`, `OPENING`, `OPEN`, `CLOSING`, `STOPPED`, `ERROR`), взаємоблокування реле та таймаути руху (>10 с).
  * **W2 — GPIO, Interrupts & Debounce:** Обробники переривань (ISR), фільтрація брязкоту контактів та захист від високочастотних імпульсних завад під час критичних операцій.
  * **W3 — UART / Serial CLI:** Парсер текстових команд (115200 baud), валідація границь параметрів (`SPEED 0..255`, `TIMEOUT 1..60`), керування станами конфігурації (`SAVED` / `DIRTY`).
  * **W4 — I2C Protocol & Bus Faults:** Низькорівневий обмін із датчиком `MPU6050`, аналіз транзакцій `ACK/NACK`, перевірка таймаутів та відновлення після втрати периферії.
  * **W5 — Recovery, WDT, Sleep & Persistence:** Сторожовий таймер (`Task WDT`, 4000 мс), енергоощадний режим `Deep Sleep`, атомарність збереження даних у NVS/Flash при раптовому зникненні живлення (`powerloss`).
  * **W6 — Python / Pytest Host Automation:** Автоматизоване тестування JSON CLI протоколу через міст `rfc2217://localhost:4000`.
  * **W7 — IoT Network Model & Memory Stability:** Програмна модель мережевого підключення та MQTT-публікацій усередині прошивки (`CONNECTED`, `DISCONNECTED`, `BACKOFF`, `CONNECTING`, команди `NET DOWN/UP`), офлайн-буфер телеметрії (8 слотів, політика `DROP_OLDEST`), дедуплікація пакетів та профілювання витоків пам'яті (`free heap`).

---

## 📂 2. Repository Structure & Evidence Package

```text
EmbededQA/
├── MASTER_TEST_PLAN.md                                      # Повний Master Test Plan проєкту (v2.0)
├── README.md                                                # Огляд портфоліо, матриця тестування та висновки
├── docs/
│   ├── Hardware_Test_Sheet_Test_Log_Obertovych.docx         # W1: Smart Gate FSM (24 TC, 4 Bugs)
│   ├── Debounce_Test_Sheet_Test_Log_Obertovych_UPDATED.docx # W2: GPIO / ISR / Debounce (7 TC, 2 Bugs)
│   ├── UART_CLI_Test_Sheet_Test_Log_Webinar_3_UPDATED.docx  # W3: UART CLI & Parser (29 TC, 6 Bugs)
│   ├── Protocol_Analysis_Sheet_Test_Log_Webinar_4.docx      # W4: I2C Bus & Logic Analyzer (1 Critical Bug)
│   ├── Recovery_Fault_Injection_Test_Sheet_Webinar_5.docx   # W5: WDT, Deep Sleep, NVS (7 Scenarios, 5 Bugs)
│   ├── Python_Pytest_Test_Sheet_Webinar_6_UPDATED.docx      # W6: Pytest CLI Triage (21 Auto-tests, 3 Bugs + 1 Obs)
│   ├── IoT_Network_Memory_Test_Sheet_Webinar_7_UPDATED.docx # W7: Network Model, Buffer & Heap (4 Bugs)
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

## ⚠️ 3. Key Quality Risks & Priority Matrix

**Легенда оцінки пріоритету ризиків (`Priority = Impact × Probability`):**
* **P0 (Blocker):** `Critical × High` — пряма загроза безпеці виконавчих механізмів, повна зупинка системи або гарантоване вичерпання пам'яті.
* **P1 (Critical):** `Critical × Medium` або `High × High` — аварійні перезавантаження МК, втрата/пошкодження даних або хибні спрацювання від перешкод.
* **P2 (Medium):** `High × Medium` або `Medium × High` — відхилення таймінгів, неоптимальний backoff, дублювання пакетів або помилки форматування.

| Risk ID | Опис ризику та потенційний наслідок | Impact | Probability | Priority | Покриття в тестах |
|---|---|---|---|---|---|
| **R-01** | **Actuator Safety Hazard:** Силові реле або ШІМ залишаються у стані `ON` після досягнення кінцевиків, таймауту руху (>10 с), команди `RESET` або перезавантаження через WDT. | Critical | High | **P0 (Blocker)** | W1 (`TC-03`, `TC-12..15`), W5 (`Relay + WDT`), W6 (`T-05`) |
| **R-02** | **ISR Noise & False Triggers:** Хибне спрацьовування виконавчих механізмів через імпульсний шум або брязкіт контактів. | High | High | **P1 (Critical)** | W2 (`TC-06`, `TC-07`), W5 (`Button`) |
| **R-03** | **CLI Buffer Overflow & Crash:** Краш прошивки (`SW_CPU_RESET`) через переповнення буфера CLI (>40 символів) або помилки парсера у стані `DIRTY`. | High | High | **P1 (Critical)** | W3 (`TC-20..23`) |
| **R-04** | **Bus Hang & Deadlock:** Повне зависання головного циклу (`Main loop`) при втраті периферії на шині I2C (`NACK`) без можливості самовідновлення. | Critical | High | **P0 (Blocker)** | W4 (`Fault Timeline`, `.vcd` trace) |
| **R-05** | **Data Corruption & Silent Loss:** Пошкодження NVS при втраті живлення (`counter: 101`) або тиха втрата пакетів телеметрії при переповненні буфера (`dropped=0`). | High | High | **P1 (Critical)** | W5 (`Interrupted save`), W7 (`Buffer Overflow`) |
| **R-06** | **Memory Leak (Heap Exhaustion):** Систематичне незворотне зменшення `free heap` під час передачі телеметрії (~80 байт на пакет). | Critical | High | **P0 (Blocker)** | W7 (`STRESS 100` × 10 ітерацій) |
| **R-07** | **Reconnect Storm & Duplication:** Занадто малий інтервал перепідключень (50 мс замість експоненційного backoff) та дублювання пакетів після офлайну. | Medium | High | **P2 (Medium)** | W7 (`NET DOWN/UP`, `Offline buffer`) |
| **R-08** | **Data Contract & Timing Drift:** Порушення контракту даних (обірваний JSON, хибні покази відключеного датчика DHT22) та відхилення таймінгів сну (`0.5 с` замість `5 с`). | High | Medium | **P2 (Medium)** | W5 (`Sensor failure`, `Sleep 5`), W6 (`T-03`) |

---

## 📊 4. Master Test Matrix & Execution Summary

Для класифікації всіх дефектів використовується єдина 4-рівнева шкала **Severity**: **Critical / High / Medium / Low**.
Загалом у межах проєкту виконано **96 перевірок**, за результатами яких підтверджено **25 дефектів прошивки** (**6 Critical**, **12 High**, **7 Medium**) та зафіксовано **1 Observation (Requirement Gap)**.

| Модуль / Вебінар | Об'єкт тестування | Всього тестів | Passed | Failed | Баги прошивки (Розбивка за Severity) | Ключові інструменти та методи |
|---|---|---:|---:|---:|---|---|
| **W1: Smart Gate Controller** | FSM, Relays, Limit Switches, Timeouts | 24 | 20 | 4 | **4** (`2 Critical`, `1 High`, `1 Medium`) | Wokwi, Arduino Uno, State Transition, Black-box |
| **W2: GPIO & Debounce** | GPIO18 ISR, Contact Bounce, Noise Injection | 7 | 5 | 2 | **2** (`2 High`) | ESP32, Wokwi Noise Generator, Interrupt Logging |
| **W3: UART / CLI** | CLI Parser, Boundaries, `SAVED/DIRTY` States | 29 | 23 | 6 | **6** (`5 High`, `1 Medium`) | Serial Monitor (115200), BVA, Equivalence Partitioning |
| **W4: I2C Protocol** | `MPU6050` (`0x68`), `SDA/SCL`, `ACK/NACK` Recovery | 3 фази | 1 | 2 | **1** (`1 Critical`) | Logic Analyzer (`.vcd`), **PulseView**, Grey-box |
| **W5: Recovery & Faults** | Deep Sleep, Task WDT, Power Loss, `DHT22` | 7 | 2 | 5 | **5** (`1 Critical`, `2 High`, `2 Medium`) | Fault Injection (`hang`, `powerloss`), Reset Reason Analysis |
| **W6: Pytest Automation** | JSON CLI API, `PING`, `GET TEMP`, `PWM 0..100` | 21 | 17 | 4 | **3** (`1 Critical`, `1 High`, `1 Medium`) + **1 Obs** | **Python 3.15.2**, **Pytest 9.2.0**, `pyserial`, `rfc2217` |
| **W7: IoT Network Model** | Reconnect Model, Offline Buffer (8), Heap Stress | 5 блоків | 1 | 4 | **4** (`1 Critical`, `1 High`, `2 Medium`) | Network State Model, `STRESS 100` Heap Profiling |
| **РАЗОМ** | **7 підсистем (W1–W7)** | **96** | **69** | **27** | **25 багів (`6 Crit`, `12 High`, `7 Med`) + 1 Obs** | **Black-box, Grey-box, Protocol Analysis, Automation** |

---

## 🐞 5. Highlighted Critical & High Bug Reports (Top Findings)

Повний реєстр усіх 25 дефектів та 1 спостереження наведено у розділі 15 документа [MASTER_TEST_PLAN.md](./MASTER_TEST_PLAN.md). Нижче виділено найважливіші знахідки:

1. **`[BUG-W4-01]` (Critical) — Повне зависання Main Loop при втраті I2C-периферії (`NACK`):**
   * **Опис:** Після активації тумблера `FAULT ON` на шині I2C фіксується `NACK` на записі адреси `0x69` (таймштамп `+5.519494 s`), а у консоль виводиться `[Wire.cpp:499] requestFrom(): i2cWriteReadNonStop returned Error -1`. Прошивка не має механізму retry/timeout і блокує основний цикл назавжди — навіть після повернення перемикача у `FAULT OFF` робота не відновлюється без повного перезапуску.

2. **`[BUG-W7-04]` (Critical) — Лінійний витік оперативної пам'яті (`Memory Leak`) під час передачі телеметрії:**
   * **Опис:** При виконанні 10 серій навантаження `STRESS 100` (1000 повідомлень у моделі мережі) обсяг вільного купа (`free heap`) монотонно та незворотно падає з `350 868` байт до `270 600` байт. Втрата становить **80 268 байт (~22.9% RAM)**, або рівно `80 байт` на кожне повідомлення.

3. **`[BUG-001]`, `[BUG-003]`, `[BUG-W5-02]` & `[BUG-W6-T05]` (Critical) — Порушення безпечного стану виконавчих механізмів:**
   * **Опис:** Силові реле у модулі воріт не вимикаються при досягненні кінцевика `LIMIT_OPEN` (`BUG-001`) та після спливання 10-секундного таймауту відкриття (`BUG-003`). У модулі W5 після спрацювання сторожового таймера (`rst:0x8 TG1WDT_SYS_RESET`) реле залишається у небезпечному стані `"relay":true` (`BUG-W5-02`). В автотесті `test_reset_restores_safe_state` команда `RESET` залишає `"led":true` та встановлює `"pwm":255` замість `0` (`BUG-W6-T05`).

4. **`[BUG-W3-22]` & `[BUG-W3-23]` (High) — Аварійне перезавантаження МК (`SYSTEM FAULT`) через парсер CLI:**
   * **Опис:** Введення рядка довжиною 41 символ (при ліміті 40) або введення неповної команди `set` у стані незбереженої конфігурації (`CONFIG=DIRTY`) призводить до крашу прошивки (`Reason: input line boundary failure` / `parser state mismatch`) та програмного скидання процесора `rst:0xc (SW_CPU_RESET)`.

5. **`[BUG-W5-03]` & `[BUG-W7-02]` (High) — Пошкодження даних у NVS та тиха втрата пакетів телеметрії:**
   * **Опис:** Зникнення живлення під час збереження (`powerloss DURING save`) призводить до появи пошкодженого стану `"counter":101` без його детектування (`BUG-W5-03`). У модулі W7 при переповненні офлайн-буфера (надсилання 9 та 12 пакетів при ємності 8) найстаріші повідомлення (`ID 1–4`) зникають, проте лічильник втрат залишається нульовим (`dropped=0`, `BUG-W7-02`).

---

## 🤖 6. Test Automation (Python + Pytest)

Автоматизований тестовий набір перевіряє роботу JSON CLI через віртуальний послідовний порт (`RFC2217` із симулятора Wokwi).

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
* **Розподіл падінь (3 Firmware Bugs + 1 Observation):**
  * `OBS-W6-T01` (`FAILED test_ping`) — `TimeoutError: No response for command: PING` *(Класифіковано як **Observation / Requirement Gap** — розбіжність контракту підтримуваних команд між тестом і прошивкою).*
  * `BUG-W6-T03` (`FAILED test_temperature_is_valid_json`) — `AssertionError: Invalid JSON from device: '{"status":"OK","temperature":24.5'` *(**High Firmware Bug** — обірваний JSON).*
  * `BUG-W6-T05` (`FAILED test_reset_restores_safe_state`) — `AssertionError: assert 255 == 0` *(**Critical Firmware Safety Bug** — небезпечний стан виходів після `RESET`).*
  * `BUG-W6-T12` (`FAILED test_pwm_valid_boundaries[100]`) — `AssertionError: assert 'ERROR' == 'OK'` *(**Medium Firmware Boundary Bug** — верхня границя `100` відхиляється).*

---

## 🛑 7. Release Decision & QA Conclusion

### **Фінальне рішення щодо релізу: ❌ NO-GO (Реліз заблоковано)**

### QA Conclusion (Підсумковий висновок)

Проведене комплексне тестування 7 модулів у середовищі симуляції Wokwi показало, що хоча базові позитивні сценарії (*Happy Path*) виконуються коректно, **прошивка містить 25 дефектів (зокрема 6 Critical та 12 High)** та не відповідає вимогам безпеки, цілісності даних і відмовостійкості:

1. **Критичні ризики безпеки (Safety Blockers — 4 Critical, 1 High):** Виконавчі механізми не захищені при аваріях. Відсутність зупинки за кінцевиком `LIMIT_OPEN` (`BUG-001`), ігнорування одночасного спрацювання кінцевиків (`BUG-002`), відсутність таймауту відкриття (`BUG-003`), збереження увімкненого реле після WDT reset (`BUG-W5-02`) та встановлення `PWM=255` після `RESET` (`BUG-W6-T05`) створюють пряму загрозу пошкодження приводу.
2. **Критичні проблеми стабільності та доступності (Availability Blockers — 2 Critical, 2 High):**
   * Відсутність обробки помилок шини I2C (`NACK`) призводить до повного зависання пристрою (`BUG-W4-01` — **Critical**).
   * Наявність лінійного витоку пам'яті (`80 байт/повідомлення`) неминуче призведе до вичерпання `free heap` (`BUG-W7-04` — **Critical**).
   * Вразливості парсера CLI викликають аварійне перезавантаження контролера при введенні 41 символу або неповної команди у стані `DIRTY` (`BUG-W3-22`, `BUG-W3-23` — **High**).
3. **Цілісність даних (Data Integrity — 4 High):** Зафіксовано тиху втрату пакетів при переповненні буфера з `dropped=0` (`BUG-W7-02`), пошкодження даних у NVS при перериванні збереження (`BUG-W5-03`), обірваний JSON у `GET TEMP` (`BUG-W6-T03`) та видачу нульових показів при відключеному датчику `DHT22` (`BUG-W5-04`).

### Необхідні кроки для досягнення статусу GO:
* Усунути всі дефекти рівнів **Critical (6 шт.)** та **High (12 шт.)**, а також узгодити специфікацію для команди `PING` (`OBS-W6-T01`).
* Реалізувати гарантоване скидання всіх GPIO/Relay/PWM у безпечний стан (`OFF`/`0`) на етапі ініціалізації після будь-якого типу перезавантаження та аварії.
* Додати таймаути та логіку повторних спроб (retry) для драйвера I2C і експоненційний backoff для моделі мережевого підключення.
* Виправити звільнення динамічної пам'яті при публікації повідомлень та забезпечити атомарність транзакцій NVS.
* Успішно пройти повний регресійний прогін Pytest (`21/21 Pass`) та провести додаткову верифікацію живлення (*brown-out*) і реального мережевого стека на фізичному мікроконтролері ESP32.