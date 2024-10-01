from fastapi import FastAPI, HTTPException
from fastapi.params import Depends
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import SessionLocal
from app.models import User, Product, Cart, CountUpdate

app = FastAPI()


async def get_db_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session

@app.put('/{user_id}/add/product/{product_id}')
async def add_product_to_cart(
        user_id: int,
        product_id: int,
        db: AsyncSession = Depends(get_db_session)
):
    user = await db.execute(select(User).where(User.id == user_id))
    user = user.scalars().one_or_none()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    product = await db.execute(select(Product).where(Product.id == product_id))
    product = product.scalars().one_or_none()

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")


    cart_item = await db.execute(select(Cart).where(Cart.user_id == user_id, Cart.product_id == product_id))
    cart_item = cart_item.scalars().one_or_none()

    if cart_item:
        cart_item.quantity += 1
        await db.commit()
        await db.refresh(cart_item)
        return cart_item
    else:
        new_cart_item = Cart(user_id=user_id, product_id=product_id)
        db.add(new_cart_item)
        await db.commit()
        await db.refresh(new_cart_item)
        return new_cart_item


@app.delete('/{user_id}/delete/product/{product_id}')
async def remove_product_from_cart(
        user_id: int,
        product_id: int,
        db: AsyncSession = Depends(get_db_session)
):
    user = await db.execute(select(User).where(User.id == user_id))
    user = user.scalars().one_or_none()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    product = await db.execute(select(Product).where(Product.id == product_id))
    product = product.scalars().one_or_none()

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    cart_item = await db.execute(select(Cart).where(Cart.user_id == user_id, Cart.product_id == product_id))
    cart_item = cart_item.scalars().one_or_none()

    if cart_item is None:
        raise HTTPException(status_code=404, detail="Cart item not found")

    await db.delete(cart_item)
    await db.commit()
    return {"detail": "Product removed from cart"}


@app.put('/{user_id}/change/product/count/{product_id}')
async def change_product_count(
        user_id: int,
        product_id: int,
        count_update: CountUpdate,
        db: AsyncSession = Depends(get_db_session)
):

    user = await db.execute(select(User).where(User.id == user_id))
    user = user.scalars().one_or_none()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    product = await db.execute(select(Product).where(Product.id == product_id))
    product = product.scalars().one_or_none()

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    cart_item = await db.execute(select(Cart).where(Cart.user_id == user_id, Cart.product_id == product_id))
    cart_item = cart_item.scalars().one_or_none()

    if cart_item is None:
        raise HTTPException(status_code=404, detail="Cart item not found")

    cart_item.quantity = count_update.count
    await db.commit()
    await db.refresh(cart_item)
    return cart_item