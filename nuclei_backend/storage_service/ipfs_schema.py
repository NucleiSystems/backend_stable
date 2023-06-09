from pydantic import BaseModel


# IpfsBase is the base class for the IpfsCreate and Ipfs classes
class IpfsBase(BaseModel):
    file_name: str
    file_size: int
    file_type: str
    file_upload_date: str


class IpfsCreate(IpfsBase):
    file_cid: str
    file_hash: str
    user: str


class Ipfs(IpfsBase):
    id: int

    class Config:
        orm_mode = True
