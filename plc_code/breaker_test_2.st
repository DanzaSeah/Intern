PROGRAM read
  VAR
    a AT %MW0 : INT;
    b AT %MW1 : INT;
    c AT %MW2 : INT;
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

