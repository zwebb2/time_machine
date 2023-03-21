"""This script will actually run the time machine"""
from machine import TimeMachine



def run(interval_seconds, verbose=False):
    """Run func for main script"""

    machine.select_data()
    machine.create_opc_server()
    machine.configure(
        interval_seconds=interval_seconds,
        verbose=verbose,
        )
    machine.configure_opc()

    machine.start_opc()
    machine.run_time_machine()

    machine.stop_opc()

if __name__ == "__main__":
    try:
        machine = TimeMachine()
        run(interval_seconds=2, verbose=True)
    except KeyboardInterrupt as error:
        print("Interrupted")
        if machine.opc_run_flag:
            machine.stop_opc()
        raise KeyboardInterrupt from error
