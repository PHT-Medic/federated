from fastapi import APIRouter, Depends, HTTPException


router = APIRouter()


@router.post("/proposal_id/discovery", response_model=DataSet)
def get_proposal(proposal_id: int) -> bool:
    dataset = datasets.get_by_name(db, name=create_msg.name)
    if dataset:
        raise HTTPException(status_code=400, detail=f"Dataset with name {create_msg.name} already exists.")
    try:
        db_dataset = datasets.create(db, obj_in=create_msg)
        if not db_dataset:
            raise HTTPException(status_code=404, detail="Error while creating new dataset.")
        return db_dataset
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Dataset file not found at {create_msg.access_path}.")
    except NotImplementedError:
        raise HTTPException(status_code=422, detail=f"Storage type {create_msg.storage_type} not possible yet.")