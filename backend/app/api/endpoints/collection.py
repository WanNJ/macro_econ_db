from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session

from ...db.database import get_db
from ...services.data_collection.controller import DataCollectionController

router = APIRouter()


@router.post("/world-bank")
def collect_world_bank_data(
    background_tasks: BackgroundTasks, db: Session = Depends(get_db)
):
    """从世界银行API采集数据（在后台运行）"""
    controller = DataCollectionController()

    # 在后台运行，以避免请求超时
    background_tasks.add_task(controller.collect_world_bank_data, db)

    return {"message": "世界银行数据采集已启动，请稍后查看结果"}


@router.post("/run-all")
def run_all_collectors(
    background_tasks: BackgroundTasks, db: Session = Depends(get_db)
):
    """运行所有数据采集器（在后台运行）"""
    controller = DataCollectionController()

    # 在后台运行，以避免请求超时
    background_tasks.add_task(controller.run_data_collection, db)

    return {"message": "数据采集已启动，请稍后查看结果"}
