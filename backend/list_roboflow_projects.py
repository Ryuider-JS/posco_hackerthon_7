"""
Roboflow 프로젝트 목록 조회
"""
import os
import sys
from dotenv import load_dotenv

# UTF-8 출력 강제
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

load_dotenv()

from roboflow import Roboflow

ROBOFLOW_API_KEY = os.getenv("ROBOFLOW_API_KEY")

print("="*80)
print("Roboflow Projects List")
print("="*80)

rf = Roboflow(api_key=ROBOFLOW_API_KEY)
workspace = rf.workspace("2025-hackerthon")

print("\nWorkspace: 2025-hackerthon")
print("\nProjects:")
print("="*80)

try:
    projects = workspace.projects()
    print(f"Type: {type(projects)}")
    print(f"Projects: {projects}")

    if isinstance(projects, list):
        for i, full_project_id in enumerate(projects, 1):
            print(f"\n[{i}] Project: {full_project_id}")

            # workspace/project-name 형식에서 project-name만 추출
            project_name = full_project_id.split('/')[-1] if '/' in full_project_id else full_project_id

            try:
                # 프로젝트 객체 가져오기
                project = workspace.project(project_name)
                print(f"    Type: {project.type}")

                # 버전 목록
                versions = project.versions()
                print(f"    Versions: {len(versions) if versions else 0}")

                if versions:
                    for v in versions:
                        print(f"      - v{v.version}: {v.name if hasattr(v, 'name') else 'unnamed'}")

                        # 모델 확인
                        try:
                            model = v.model
                            if model:
                                print(f"        [OK] Model available!")
                                print(f"        Model ID: {project_id}/{v.version}")
                            else:
                                print(f"        [X] No model trained")
                        except:
                            print(f"        [X] No model trained")

            except Exception as e:
                print(f"    Error: {e}")
    else:
        print("Unexpected format!")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
