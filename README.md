# 1.导入数据后，执行以下语句
select setval('tables_prorelations_id_seq',(SELECT max(id) FROM "tables_prorelations"));

select setval('tables_research_id_seq',(SELECT max(id) FROM "tables_research"));

select setval('tables_projects_id_seq',(SELECT max(id) FROM "tables_projects"));

select setval('tables_user_id_seq',(SELECT max(id) FROM "tables_user"));

select setval('tables_user_groups_id_seq',(SELECT max(id) FROM "tables_user_groups"));

select setval('tables_userbehavior_id_seq',(SELECT max(id) FROM "tables_userbehavior"));

select setval('tables_userclickbehavior_id_seq',(SELECT max(id) FROM "tables_userclickbehavior"));

select setval('tables_userdownloadbehavior_id_seq',(SELECT max(id) FROM "tables_userdownloadbehavior"));

select setval('tables_participant_id_seq',(SELECT max(id) FROM "tables_participant"));

select setval('tables_orgnature_id_seq',(SELECT max(id) FROM "tables_orgnature"));

select setval('tables_organization_id_seq',(SELECT max(id) FROM "tables_organization"));

select setval('tables_limitnums_id_seq',(SELECT max(id) FROM "tables_limitnums"));

select setval('tables_hotwords_id_seq',(SELECT max(id) FROM "tables_hotwords"));

select setval('tables_classify_cls_id_seq',(SELECT max(cls_id) FROM "tables_classify"));

select setval('tables_bid_id_seq',(SELECT max(id) FROM "tables_bid"));

select setval('auth_group_id_seq',(SELECT max(id) FROM "auth_group"));

select setval('tables_sensitivewords_id_seq',(SELECT max(id) FROM "tables_sensitivewords"));

# 2.更新机构表中的成果总数
truncate ttt;
insert into ttt(org_id, pro_sum)
-- select organization_id, count(projects_id) from tables_projects_lead_org,tables_projects where tables_projects_lead_org.projects_id=tables_projects.id and tables_projects.status=1
-- group by organization_id;
select organization_id, count(projects_id) from tables_projects_research,tables_projects  where tables_projects_research.projects_id=tables_projects.id and tables_projects.status=1
group by organization_id;
-- update tables_organization set pro_sum=0;
update tables_organization set pro_sum=ttt.pro_sum from ttt where ttt.org_id=tables_organization.id
-- 重复项处理
select distinct(organization_id) from tables_projects_research where organization_id in (select organization_id from tables_projects_lead_org)
# 3.更新机构表中的研究人员总数
truncate ttt;
insert into ttt(org_id,pro_sum)
SELECT unit_id,count(id) FROM "tables_participant" where is_show=True and unit_id is not null group by unit_id;
update tables_organization set par_sum=0;
update tables_organization set par_sum=ttt.pro_sum from ttt where ttt.org_id=tables_organization.id;

# 更新人员表中的成果数量
truncate ttt;
insert into ttt(org_id, pro_sum)
select par_id,count(id) from tables_prorelations where is_eft='t' group by(par_id) having par_id is not null order by par_id;
update tables_participant set pro_sum=ttt.pro_sum from ttt where ttt.org_id=tables_participant.id