-- IntelHealth: 症状数据种子文件
-- 在 Supabase SQL Editor 中执行此文件来填充 symptoms 表
-- 表结构: id (text, 主键), name (text), body_part (text), description (text)

-- 先清空旧数据（如果有）
DELETE FROM symptoms;

-- 头部症状
INSERT INTO symptoms (id, name, body_part, description) VALUES
(gen_random_uuid()::text, '头痛', 'head', '头部疼痛，可能伴有压迫感、跳痛或钝痛'),
(gen_random_uuid()::text, '头晕', 'head', '眩晕感或失去平衡感，可能伴有旋转感'),
(gen_random_uuid()::text, '偏头痛', 'head', '单侧头部搏动性疼痛，常伴恶心、畏光'),
(gen_random_uuid()::text, '耳鸣', 'head', '耳内持续嗡嗡声或铃声，无外界声源'),
(gen_random_uuid()::text, '视力模糊', 'head', '看东西不清晰，可能是突发或渐进性的'),
(gen_random_uuid()::text, '面部疼痛', 'head', '面部一侧或双侧的疼痛或压迫感'),
(gen_random_uuid()::text, '记忆力下降', 'head', '近期记忆减退或注意力难以集中'),
(gen_random_uuid()::text, '失眠', 'head', '难以入睡或睡眠质量差');

-- 胸部症状
INSERT INTO symptoms (id, name, body_part, description) VALUES
(gen_random_uuid()::text, '胸痛', 'chest', '胸部不适、压迫感或疼痛，可能向手臂放射'),
(gen_random_uuid()::text, '呼吸困难', 'chest', '呼吸急促、费力或感到无法获取足够空气'),
(gen_random_uuid()::text, '心悸', 'chest', '心跳加速、不规则或感到心脏跳动明显'),
(gen_random_uuid()::text, '咳嗽', 'chest', '持续或间歇性咳嗽，可能有痰或无痰'),
(gen_random_uuid()::text, '咳血', 'chest', '咳嗽时带有血丝或咳出血液'),
(gen_random_uuid()::text, '胸闷', 'chest', '胸部沉重压迫感，感觉透不过气'),
(gen_random_uuid()::text, '喉咙痛', 'chest', '吞咽时喉咙疼痛、干燥或灼热感'),
(gen_random_uuid()::text, '气喘', 'chest', '呼吸时伴有喘息声，呼气困难');

-- 腹部症状
INSERT INTO symptoms (id, name, body_part, description) VALUES
(gen_random_uuid()::text, '腹痛', 'abdomen', '腹部各区域的不适或疼痛，可能是钝痛或绞痛'),
(gen_random_uuid()::text, '恶心', 'abdomen', '想吐的感觉，可能伴有头晕、出汗'),
(gen_random_uuid()::text, '呕吐', 'abdomen', '胃内容物通过口腔强制排出'),
(gen_random_uuid()::text, '腹泻', 'abdomen', '排便次数增加，粪便稀薄或含水量高'),
(gen_random_uuid()::text, '便秘', 'abdomen', '排便困难、不规则或频率减少'),
(gen_random_uuid()::text, '腹胀', 'abdomen', '腹部膨胀感，常伴有嗳气或排气增多'),
(gen_random_uuid()::text, '食欲不振', 'abdomen', '进食欲望明显下降或完全没有食欲'),
(gen_random_uuid()::text, '胃灼热', 'abdomen', '胸骨后或上腹部烧灼感，常于饭后加重');

-- 背部症状
INSERT INTO symptoms (id, name, body_part, description) VALUES
(gen_random_uuid()::text, '背痛', 'back', '背部任何区域的疼痛，可能是突发或慢性的'),
(gen_random_uuid()::text, '腰痛', 'back', '腰部疼痛，弯腰或久坐后可能加重'),
(gen_random_uuid()::text, '脊椎僵硬', 'back', '脊椎活动受限，晨起时尤为明显'),
(gen_random_uuid()::text, '肩颈疼痛', 'back', '肩部和颈部肌肉疼痛、僵硬或紧张'),
(gen_random_uuid()::text, '坐骨神经痛', 'back', '从腰部沿臀部、大腿后侧向下放射的疼痛'),
(gen_random_uuid()::text, '驼背', 'back', '脊柱弯曲异常，上背部隆起');

-- 手臂症状
INSERT INTO symptoms (id, name, body_part, description) VALUES
(gen_random_uuid()::text, '关节痛', 'arms', '关节区域疼痛、僵硬或肿胀，影响活动'),
(gen_random_uuid()::text, '手指麻木', 'arms', '手指感觉减退或有刺痛感'),
(gen_random_uuid()::text, '手臂无力', 'arms', '手臂力量明显下降，抓握困难'),
(gen_random_uuid()::text, '手部肿胀', 'arms', '手部或手腕区域明显肿胀'),
(gen_random_uuid()::text, '肘部疼痛', 'arms', '肘关节疼痛，可能活动时加重'),
(gen_random_uuid()::text, '手抖', 'arms', '手部不自主震颤，静止或活动时出现');

-- 腿部症状
INSERT INTO symptoms (id, name, body_part, description) VALUES
(gen_random_uuid()::text, '腿痛', 'legs', '腿部疼痛，可能影响行走或站立'),
(gen_random_uuid()::text, '膝盖疼痛', 'legs', '膝关节疼痛、肿胀或活动受限'),
(gen_random_uuid()::text, '腿部水肿', 'legs', '腿部或脚踝明显肿胀，按压后凹陷'),
(gen_random_uuid()::text, '小腿抽筋', 'legs', '小腿肌肉突然痉挛，伴剧烈疼痛'),
(gen_random_uuid()::text, '脚趾麻木', 'legs', '脚趾感觉减退或有针刺感'),
(gen_random_uuid()::text, '行走困难', 'legs', '步态不稳或无法正常行走');

-- 皮肤症状
INSERT INTO symptoms (id, name, body_part, description) VALUES
(gen_random_uuid()::text, '皮疹', 'skin', '皮肤上出现红斑、丘疹或水疱等异常变化'),
(gen_random_uuid()::text, '瘙痒', 'skin', '皮肤上引起抓挠欲望的不适感'),
(gen_random_uuid()::text, '皮肤干燥', 'skin', '皮肤缺水脱屑，可能伴有紧绷感'),
(gen_random_uuid()::text, '痤疮', 'skin', '面部或身体出现粉刺、脓疱等痤疮表现'),
(gen_random_uuid()::text, '荨麻疹', 'skin', '皮肤出现风团，瘙痒明显，时起时消'),
(gen_random_uuid()::text, '皮肤变色', 'skin', '皮肤局部颜色发生异常变化'),
(gen_random_uuid()::text, '伤口不愈', 'skin', '伤口或溃疡长时间无法正常愈合'),
(gen_random_uuid()::text, '脱发', 'skin', '头发异常脱落或变薄');

-- 全身症状
INSERT INTO symptoms (id, name, body_part, description) VALUES
(gen_random_uuid()::text, '发热', 'general', '体温升高（超过37.5°C），可能伴有出汗或寒战'),
(gen_random_uuid()::text, '疲劳', 'general', '全身无力、乏力或精力不足'),
(gen_random_uuid()::text, '体重减轻', 'general', '非故意的体重下降，短时间内明显减轻'),
(gen_random_uuid()::text, '体重增加', 'general', '明显的体重增加，可能伴有水肿'),
(gen_random_uuid()::text, '肌肉痛', 'general', '全身肌肉疼痛或酸痛'),
(gen_random_uuid()::text, '睡眠问题', 'general', '难以入睡、频繁醒来或睡眠质量差'),
(gen_random_uuid()::text, '盗汗', 'general', '夜间大量出汗，常湿透衣物或床单'),
(gen_random_uuid()::text, '淋巴结肿大', 'general', '颈部、腋下或腹股沟淋巴结可触及肿大');
