from .quota_models import UserQuota
import datetime


def initialise_quota(user_id, db):
    quota_init = UserQuota(
        user_quota=0,
        last_update=str(datetime.datetime.now()),
        amount_of_files=0,
        owner_id=user_id,
    )
    db.add(quota_init)
    db.commit()


def increase_quota(user_id, db, increase_amount, files_being_committed):
    current_quota = get_current_quota(user_id, db)

    current_quota.user_quota = current_quota.user_quota + increase_amount
    current_quota.last_update = str(datetime.datetime.now())
    current_quota.amount_of_files = (
        current_quota.amount_of_files + files_being_committed
    )
    current_quota.owner_id = user_id
    db.commit()


def decrease_quota(user_id, db, decrease_amount, files_being_deleted):
    current_quota = get_current_quota(user_id, db)

    decreasing_query = UserQuota(
        user_quota=current_quota.user_quota - decrease_amount,
        last_update=str(datetime.datetime.now()),
        amount_of_files=current_quota.amount_of_files - files_being_deleted,
        owner_id=user_id,
    )

    db.add(decreasing_query)
    db.commit()


def get_current_quota(user_id, db):
    query = db.query(UserQuota).filter(UserQuota.owner_id == user_id).first()
    return query
