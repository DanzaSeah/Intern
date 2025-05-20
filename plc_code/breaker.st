PROGRAM ied_read
  VAR
    current_0 at %QW100
    line_cb_0 AT %QW101 : INT;
  END_VAR
  VAR
    test : BOOL := false;
  END_VAR

  IF current_0 > 100 THEN
    test := false;
  ELSE
    test := true;
  END_IF;

END_PROGRAM

CONFIGURATION Config0
    RESOURCE Res0 ON PLC
        TASK Task0(INTERVAL := T#10ms, PRIORITY := 1);
        PROGRAM Inst0 WITH Task0 : ied_read;
    END_RESOURCE
END_CONFIGURATION