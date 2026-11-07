-- 누구세요? 화면은 출입증 없이 연다. 익명 사용자는 비밀번호를 낼 때만 만든다
-- (링크 미리보기 봇·그냥 열어 본 사람마다 사용자를 만들면 익명 가입 한도에 걸린다).
-- sp_entry_info는 링크를 가진 사람에게 보여 줄 정보만 돌려주므로 anon에 연다.
grant execute on function public.sp_entry_info(text) to anon;
