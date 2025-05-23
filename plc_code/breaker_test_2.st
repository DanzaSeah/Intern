PROGRAM read
  VAR
    a AT %QW100 : INT;
    b AT %QW101 : INT;
    c AT %QW102 : INT;
  END_VAR
  VAR
    test : BOOL := false;
    Tripvalue : INT := 1000;
  END_VAR

  c := 1;

END_PROGRAM

CONFIGURATION Config0
    RESOURCE Res0 ON PLC
        TASK Task0(INTERVAL := T#20ms, PRIORITY := 0);
        PROGRAM instance0 WITH task0 : read;
    END_RESOURCE
END_CONFIGURATION

