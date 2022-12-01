# import potrzebnych modułów

import time
import random
import os
import sys

# zmienne do zarządzania przebiegiem symulacji

maxTimeOn = 12  # maksymalny czas jazdy w symulacji
maxTimeOff = 4  # maksymalny czas jednostajnego postoju
minTimeOn = 3  # minimalny czas jazdy do wykonania pomiarów
sampling = 0.1  # próbkowanie pomiarów
simDuration = 60  # długość trwania całej symulacji
peakPiezoVoltage = 150  # maksymalne napięcie możliwe do wygenerowania w Piezo (cały układ) [V]
piezoCapacity = 4000  # pojemność Piezo (cały układ) [uF]

# zmienne pomocnicze

path = os.path.dirname(os.path.abspath(__file__))
filename = os.path.join(
    path, time.strftime("%Y%m%d_%H_%M_%S", time.localtime()) + ".txt"
)
lowestPiezoVoltage = int(peakPiezoVoltage / 10)
wasStill = True
simStartTime = int(time.perf_counter())
startDate = time.strftime("%d.%m.%Y     %H:%M:%S", time.localtime())
overallSuppliedPower = 0
overallExaminationTime = 0

# utworzenie pliku logowania wyników z obługą błędów

try:
    with open(filename, "w") as file:
        file.write("Rozpoczęcie symulacji\n" + startDate + "\n" + 60 * "-")
except:
    print("Nie udało się utworzyć pliku", sys.exc_info()[0])

# rozpoczęcie symulacji - nieskończona pętla z przerwaniem po przekroczeniu zadanego czasu

while True:
    onOff = True if wasStill == True else False
    actualSimTime = int(time.perf_counter())
    if actualSimTime - simStartTime >= simDuration:
        break

    # Warunkowe rozróżnienie jazda/postój. Jeżeli auto porusza się przez czas większy od minimalnego czasu do pomiarów (zadany) dokonywane jest przypadkowe
    # generowanie wstrząsów o przypadkowej częstotliwości i amplitudzie (próbkowanie zadane na początku programu). Pomiar jest wykonywany w przypadkowo
    # wygenerowanym czasie w przedziale zadanym na początku programu.

    # Jeżeli auto nie będzie poruszać się wystarczająco długo pomiar zostanie anulowany (wyświetlony zostanie stosowny komunikat.

    # Jeżeli auto jest na postoju zostanie wyświetlony stosowny komunikat a pomar nie będzie zbierany.

    # Samochód na zmianę jedzie i zatrzymuje się, czasu są losowe w zadanych przedziałach.

    elif onOff:
        randomTimeOn = random.randint(1, maxTimeOn)
        wasStill = False
        if randomTimeOn >= minTimeOn:
            start = int(time.perf_counter())
            voltageSum = 0
            pulsesAmount = 0
            while True:
                ifPulse = random.randint(0, 1)
                if ifPulse:
                    simulatedVoltage = random.randint(
                        lowestPiezoVoltage, peakPiezoVoltage
                    )
                    voltageSum += simulatedVoltage
                    pulsesAmount += 1
                    time.sleep(sampling)
                    stop = int(time.perf_counter())
                else:
                    time.sleep(sampling)
                    stop = int(time.perf_counter())

                if stop - start >= randomTimeOn:
                    break
                else:
                    continue

            # Oblczenia wartości na podstawie pomiarów oraz ich zapis do pliku.
            # Zależności dla przebiegu trójkątnego - przyjęto na podstawie pomiarów oscyloskopem na układzie w skali mikro.

            avgVoltage = voltageSum / pulsesAmount
            freq = pulsesAmount / randomTimeOn
            RMSVoltage = avgVoltage / (2 * 3 ** (1 / 3))
            RMSCurrent = avgVoltage * 2 * freq * piezoCapacity * 0.000001
            suppliedPower = RMSCurrent * RMSVoltage
            heatDissipation = suppliedPower * 0.1
            overallSuppliedPower += suppliedPower
            overallExaminationTime += randomTimeOn

            tempText = (
                """\nWyniki:
                  Czas próby: {} sek
                  Średnie napięcie w peaku: {:.3f} V
                  Częstotliwość wstrząsów w próbie: {:.3f} Hz
                  Napięcie RMS: {:.3f} V
                  Prąd RMS: {:.3f} A
                  Straty ciepne: {:.3f} W
                  Dostarczona moc ładowania: {:.3f} W\n""".format(
                    randomTimeOn,
                    avgVoltage,
                    freq,
                    RMSVoltage,
                    RMSCurrent,
                    heatDissipation,
                    suppliedPower,
                )
                + 60 * "-"
            )

            try:
                with open(filename, "a") as file:
                    for line in tempText:
                        file.write(line)
            except:
                print("Nie udało się dopisać danych do pliku", sys.exc_info()[0])

            print(tempText)

        else:
            time.sleep(float(randomTimeOn))
            tempText = (
                "\nZa krótki czas jazdy - {} sek\n".format(randomTimeOn) + 60 * "-"
            )
            wasStill = False

            try:
                with open(filename, "a") as file:
                    for line in tempText:
                        file.write(line)
            except:
                print("Nie udało się dopisać danych do pliku", sys.exc_info()[0])

            print(tempText)

    else:
        randomTimeOff = random.randint(1, maxTimeOff)
        time.sleep(float(randomTimeOff))
        tempText = "\nPostój - {} sek\n".format(randomTimeOff) + 60 * "-"
        wasStill = True

        try:
            with open(filename, "a") as file:
                for line in tempText:
                    file.write(line)
        except:
            print("Nie udało się dopisać danych do pliku", sys.exc_info()[0])

        print(tempText)

# Zapis do pliku całej mocy zebranej podczas symulacji oraz uśrednienie na cały czas, w którym zbierane były pomiary

avgPower = overallSuppliedPower / overallExaminationTime * 60
stopDate = time.strftime("%d.%m.%Y     %H:%M:%S", time.localtime())
tempText = """\nŁączna moc wygenerowana w trakcie symulacji: {:.3f} W
Średnia ilość generowanej mocy na minutę jazdy: {:.3f} W/min

Symulacja zakończona
{}""".format(
    overallSuppliedPower, avgPower, stopDate
)

try:
    with open(filename, "a") as file:
        for line in tempText:
            file.write(line)
except:
    print("Nie udało się dopisać danych do pliku", sys.exc_info()[0])
