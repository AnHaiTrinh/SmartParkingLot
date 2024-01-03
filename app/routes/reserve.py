import json
from datetime import datetime

from fastapi import APIRouter, status, HTTPException
from ..models.schemas import ReserveOrder
from ..dependencies.kafka import KafkaProducerDependency

router = APIRouter(
    prefix='/reserve',
    tags=['reserve']
)


@router.post('/', status_code=status.HTTP_204_NO_CONTENT)
def reserve_space(
        reserve_order: ReserveOrder,
        kafka_producer: KafkaProducerDependency
):
    exception = None

    def acked(err, msg):
        if err is not None:
            nonlocal exception
            print(f"Failed to deliver message {msg}: {err}")
            exception = HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                      detail='Failed to reserve space')

    message = reserve_order.model_dump()
    message['updated_at'] = datetime.now()
    message['state'] = 'reserved'
    kafka_producer.produce(
        topic='parking_space_state_raw',
        key=str(reserve_order.parking_space_id),
        value=json.dumps(message),
        callback=acked
    )
    kafka_producer.poll(1)
    if exception:
        raise exception
    return
