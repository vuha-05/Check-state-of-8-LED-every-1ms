# Overview
This project continuously monitors the on/off states of 8 LEDs (or 8 digital output pins) at 1-millisecond interval. The collected state data is immediately transmitted to a PC via UART. 

# Hardware
- STM32F103C8T6 (Blue Pill)
- USB-to-RS232 converter cable
- RS232 To UART TTL converter module
- 10-Bit Dip Switch, emulator for 8 led lights, remember to connect their ground 

# Pinout Configuration
- PA0 - PA7 (GPIO Output/Input) Connected to 8 LEDs. 
- PA9 (USART1_TX)
- PA10 (USART1_RX)

# Tools
- STM32CubeIDE
- STM32CubeMX

