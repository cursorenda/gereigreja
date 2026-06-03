from django.db import migrations, models


EBD_PONTOS_DEFAULT = {
    'presente': 10,
    'biblia': 2,
    'revista': 2,
    'oferta': 3,
    'visitante': 5,
}


def _valor_cfg(igreja, campo, fallback):
    valor = getattr(igreja, campo, None)
    return fallback if valor is None else int(valor)


def _calcular_pontos(freq, cfg):
    total = 0
    if freq.presente:
        total += cfg['presente']
    if freq.trouxe_biblia:
        total += cfg['biblia']
    if freq.trouxe_revista:
        total += cfg['revista']
    if freq.trouxe_oferta:
        total += cfg['oferta']
    if freq.trouxe_visitante:
        total += cfg['visitante']
    return total


def backfill_pontos_total(apps, schema_editor):
    Frequencia = apps.get_model('escola_biblica', 'Frequencia')
    Turma = apps.get_model('escola_biblica', 'Turma')
    Igreja = apps.get_model('configuracao', 'Igreja')
    Membro = apps.get_model('secretaria', 'Membro')

    qs_null = Frequencia.objects.filter(pontos_total__isnull=True)
    turma_ids = list(qs_null.values_list('aluno__turma_id', flat=True).distinct())
    if not turma_ids:
        return

    turmas = Turma.objects.filter(id__in=turma_ids).select_related('igreja', 'classe__igreja')

    turma_para_igreja = {}
    turmas_sem_igreja = []
    for turma in turmas:
        igreja = turma.igreja or getattr(turma.classe, 'igreja', None)
        if igreja is None:
            turmas_sem_igreja.append(turma.id)
        else:
            turma_para_igreja[turma.id] = igreja.id

    if turmas_sem_igreja:
        through = Turma.membros.through
        pares = through.objects.filter(turma_id__in=turmas_sem_igreja).values_list('turma_id', 'membro_id')
        membro_ids = sorted({membro_id for _, membro_id in pares})
        igreja_por_membro = {
            m['id']: m['igreja_id']
            for m in Membro.objects.filter(id__in=membro_ids).values('id', 'igreja_id')
            if m['igreja_id'] is not None
        }
        for turma_id, membro_id in pares:
            if turma_id in turma_para_igreja:
                continue
            igreja_id = igreja_por_membro.get(membro_id)
            if igreja_id is not None:
                turma_para_igreja[turma_id] = igreja_id

    igreja_ids = sorted(set(turma_para_igreja.values()))
    igrejas_cfg = {}
    if igreja_ids:
        for igreja in Igreja.objects.filter(id__in=igreja_ids):
            igrejas_cfg[igreja.id] = {
                'presente': _valor_cfg(igreja, 'ebd_pontos_presente', EBD_PONTOS_DEFAULT['presente']),
                'biblia': _valor_cfg(igreja, 'ebd_pontos_biblia', EBD_PONTOS_DEFAULT['biblia']),
                'revista': _valor_cfg(igreja, 'ebd_pontos_revista', EBD_PONTOS_DEFAULT['revista']),
                'oferta': _valor_cfg(igreja, 'ebd_pontos_oferta', EBD_PONTOS_DEFAULT['oferta']),
                'visitante': _valor_cfg(igreja, 'ebd_pontos_visitante', EBD_PONTOS_DEFAULT['visitante']),
            }

    updates = []
    frequencias = qs_null.select_related('aluno__turma').only(
        'id',
        'presente',
        'trouxe_biblia',
        'trouxe_revista',
        'trouxe_oferta',
        'trouxe_visitante',
        'aluno__turma_id',
    )
    for freq in frequencias.iterator(chunk_size=2000):
        turma_id = freq.aluno.turma_id
        igreja_id = turma_para_igreja.get(turma_id)
        cfg = igrejas_cfg.get(igreja_id, EBD_PONTOS_DEFAULT)
        freq.pontos_total = _calcular_pontos(freq, cfg)
        updates.append(freq)
        if len(updates) >= 2000:
            Frequencia.objects.bulk_update(updates, ['pontos_total'], batch_size=1000)
            updates = []

    if updates:
        Frequencia.objects.bulk_update(updates, ['pontos_total'], batch_size=1000)


def noop_reverse(apps, schema_editor):
    return


class Migration(migrations.Migration):

    dependencies = [
        ('escola_biblica', '0027_frequencia_pontos_total'),
    ]

    operations = [
        migrations.RunPython(backfill_pontos_total, noop_reverse),
        migrations.AddIndex(
            model_name='frequencia',
            index=models.Index(fields=['data', 'aluno'], name='ebd_freq_data_aluno_idx'),
        ),
        migrations.AddIndex(
            model_name='frequencia',
            index=models.Index(fields=['data', 'presente'], name='ebd_freq_data_pres_idx'),
        ),
    ]
