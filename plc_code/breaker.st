PROGRAM ied_read
  VAR  
    bus_voltage_0 AT %IW100 : INT;
    current_0 AT %IW101 : INT;
    line_cb_0 AT %QW100 : INT;
  END_VAR
  VAR
    test : BOOL := false;
    Tripvalue : INT := 1000;
  END_VAR

  IF TRUE THEN
    line_cb_0 := 1 - line_cb_0;
  END_IF;

END_PROGRAM

CONFIGURATION Config0
    RESOURCE Res0 ON PLC
        TASK Task0(INTERVAL := T#2000ms, PRIORITY := 0);
        PROGRAM Inst0 WITH Task0 : ied_read;
    END_RESOURCE
END_CONFIGURATION
