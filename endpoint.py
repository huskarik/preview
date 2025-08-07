@router.put("/{account_id}")
async def update_vendor_user_state(
        account_id: str,
        data: VendorActivate,
        token_payload: dict = Depends(validate_ms_jwt_token),
        session: AsyncSession = Depends(db_helper.session_getter),
):
    service = VendorService(session)
    state = await service.update_state(account_id, data)

    return {"status": state}
