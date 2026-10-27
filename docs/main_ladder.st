PROGRAM main
  VAR
    ready : BOOL;
  END_VAR
  VAR
    open_pb AT %IX0.0 : BOOL;
    close_pb AT %IX0.1 : BOOL;
    stob_pb AT %IX0.2 : BOOL;
    top_limit AT %MX0.0 : BOOL;
    bottom_limit AT %MX0.1 : BOOL;
    motor_up AT %QX0.0 : BOOL;
    motor_down AT %QX0.1 : BOOL;
    open_lamp AT %QX0.2 : BOOL;
    shut_lamp AT %QX0.3 : BOOL;
    ajar_lamp AT %QX0.4 : BOOL;
    remote_open AT %MX0.2 : BOOL;
  END_VAR

  motor_up := NOT(motor_down) AND NOT(top_limit) AND NOT(stob_pb) AND (motor_up OR open_pb OR remote_open);
  motor_down := NOT(motor_up) AND NOT(bottom_limit) AND NOT(stob_pb) AND (motor_down OR ready AND close_pb);
  open_lamp := top_limit;
  shut_lamp := bottom_limit;
  ajar_lamp := NOT(bottom_limit) AND NOT(top_limit);
  IF NOT(stob_pb) AND NOT(remote_open) AND NOT(close_pb) AND NOT(open_pb) AND NOT(motor_down) AND NOT(motor_up) THEN
    ready := TRUE; (*set*)
  END_IF;
  IF motor_down OR motor_up THEN
    ready := FALSE; (*reset*)
  END_IF;
END_PROGRAM


CONFIGURATION Config0

  RESOURCE Res0 ON PLC
    TASK task0(INTERVAL := T#20ms,PRIORITY := 1);
    PROGRAM instance0 WITH task0 : main;
  END_RESOURCE
END_CONFIGURATION
