PROGRAM ied_read
  VAR
    bus_voltage_0 AT %MW0 : INT;
    current_0 AT %MW1 : INT;
    line_cb_0 AT %MW2 : INT;
  END_VAR

  line_cb_0 := 1;

END_PROGRAM

CONFIGURATION Config0
    RESOURCE Res0 ON PLC
        TASK Task0(INTERVAL := T#20ms, PRIORITY := 0);
        PROGRAM instance0 WITH task0 : ied_read;
    END_RESOURCE
END_CONFIGURATION

