create table denormalized_tweets as (
    select * from conversations
    left join (
        select auth.id as author_id,
        auth.name as author_name,
        auth.username as author_username,
        auth.description as author_description,
        auth.followers_count as author_followers_count,
        auth.following_count as author_following_count,
        auth.tweet_count as author_tweet_count,
        auth.listed_count as author_listed_count
        from authors as auth
    ) authors using(author_id)
    left join (
        select anno.conversation_id as "id",
        array_agg(anno.id) as annotations_id,
        array_agg(anno.value) as annotations_values,
        array_agg(anno.type) as annotations_types,
        array_agg(anno.probability) as annotations_probabilities
        from annotations as anno
        group by anno.conversation_id
    ) annotations using("id")
    left join (
		select cont_anno.conversation_id as "id",
        array_agg(cont_dom.id) as domain_ids,
        array_agg(cont_dom.name) as domain_names,
        array_agg(cont_dom.description) as domain_descriptions,
        array_agg(cont_ent.id) as entity_ids,
        array_agg(cont_ent.name) as entity_names,
        array_agg(cont_ent.description) as entity_descriptions
        from context_annotations as cont_anno
		left join context_domains as cont_dom on cont_dom.id = cont_anno.context_domain_id
		left join context_entities as cont_ent on cont_ent.id = cont_anno.context_entity_id
		group by cont_anno.conversation_id
	) context_annotations using("id")
    left join (
		select lnk.conversation_id as "id",
        array_agg(lnk.id) as link_ids,
        array_agg(lnk.title) as link_titles,
        array_agg(lnk.url) as link_urls,
        array_agg(lnk.description) as link_descriptions
        from links as lnk
		group by lnk.conversation_id
	) links using("id")
    left join (
		select conv_hash.conversation_id as "id",
        array_agg(hsh.id) as hashtag_ids,
        array_agg(hsh.tag) as hashtag_tags
        from conversation_hashtags as conv_hash
	    left join hashtags as hsh
        on hsh.id = conv_hash.hashtag_id
	    group by conv_hash.conversation_id
	) hashtags using("id")
    left join (
        select conv_ref.conversation_id as "id",
        array_agg(conv_ref.parent_id) as conversation_reference_parent_ids,
        array_agg(conv_ref.type) as conversation_reference_types
        from conversation_references as conv_ref
        group by conv_ref.conversation_id
    ) conversation_references using("id")
)