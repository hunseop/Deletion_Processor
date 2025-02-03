import logging
from config import TASK_MENU
from processors import PolicyProcessor

def select_task():
    """작업 선택 메뉴"""
    print("\n시작할 작업 번호를 입력해주세요.")
    for task_id, task_name in TASK_MENU.items():
        print(f"{task_id}. {task_name}")

    while True:
        try:
            choice = int(input("\n작업 번호 (1-8, 종료: 0): "))
            if choice in TASK_MENU:
                return choice
            else:
                print('유효하지 않은 번호입니다.')
        except ValueError:
            print("올바른 숫자를 입력해주세요.")

def main():
    """메인 프로그램"""
    processor = PolicyProcessor()
    
    try:
        logging.info("Starting deletion process")
        while True:
            choice = select_task()
            
            if choice == 0:
                logging.info("Exiting deletion process")
                break
                
            try:
                if choice == 1:
                    processor.parse_request_type()
                elif choice == 2:
                    processor.extract_request_id()
                elif choice == 3:
                    processor.add_request_info()
                elif choice == 4:
                    processor.process_exceptions(vendor='paloalto')
                elif choice == 5:
                    processor.process_exceptions(vendor='secui')
                elif choice == 6:
                    processor.organize_redundant_file()
                elif choice == 7:
                    processor.notice_file_organization()
                elif choice == 8:
                    processor.add_mis_id()
                
            except Exception as e:
                logging.error(f"Error processing task {choice}: {str(e)}")
                print(f"작업 처리 중 오류가 발생했습니다: {str(e)}")
                continue

    except Exception as e:
        logging.exception(f"Fatal error in main process: {str(e)}")
    finally:
        logging.info("Program terminated")

if __name__ == "__main__":
    main() 