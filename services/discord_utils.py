def get_member_name(member):

    return (
        member.nick
        or member.global_name
        or member.name
    )