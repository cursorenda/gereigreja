from django.core.management.base import BaseCommand
import json
import traceback


class Command(BaseCommand):
    help = 'Test create visitante via internal client'

    def handle(self, *args, **options):
        # Use RequestFactory and call the view directly so exceptions are raised
        # as Python tracebacks (instead of Django rendering the HTML debug page)
        try:
            from django.test import RequestFactory
            from django.contrib.auth import get_user_model
            from secretaria.views import criar_visitante_parcial
            from secretaria.utils import get_allowed_churches_for_membros
            from django.conf import settings
            User = get_user_model()
        except Exception as e:
            self.stdout.write('IMPORT ERROR: %s' % e)
            traceback.print_exc(file=self.stdout)
            return

        try:
            # Prefer an active non-superuser who has a perfil with an active ministerio
            candidates = User.objects.filter(is_active=True, is_superuser=False)
            user = None
            for u in candidates:
                try:
                    perfil = getattr(u, 'perfil', None)
                    ministerio = getattr(perfil, 'ministerio', None) if perfil is not None else None
                    if ministerio and getattr(ministerio, 'ativo', False):
                        user = u
                        break
                except Exception:
                    continue
            # Fallback: any active non-superuser
            if not user:
                user = candidates.first()
        except Exception as e:
            self.stdout.write('DB QUERY ERROR when fetching user: %s' % e)
            traceback.print_exc(file=self.stdout)
            return

        if not user:
            self.stdout.write('NO_ACTIVE_NON_SUPERUSER_FOUND')
            return

        try:
            rf = RequestFactory()
            payload = {'nome': 'Teste Visitante Automático', 'apelido': 'TstAuto'}
            # Mark as AJAX to exercise the JSON response code path
            request = rf.post('/sistema/visitantes/criar-parcial/', data=payload, **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
            # Attach a real user and minimal attributes the view expects
            request.user = user
            # Provide igreja_ativa if available via allowed churches helper
            try:
                allowed = get_allowed_churches_for_membros(user)
                if getattr(allowed, 'exists', None) and allowed.exists():
                    request.igreja_ativa = allowed.first()
            except Exception:
                request.igreja_ativa = None

            # Call the view directly and print the returned JsonResponse or raise exception
            try:
                resp = criar_visitante_parcial(request)
            except Exception as e:
                self.stdout.write('VIEW RAISED EXCEPTION: %s' % e)
                traceback.print_exc(file=self.stdout)
                return

            # If we created a visitante successfully, attempt to register presence via ajax_registrar_presenca_evento
            try:
                parsed = None
                try:
                    content = getattr(resp, 'content', b'').decode('utf-8')
                    parsed = json.loads(content)
                except Exception:
                    parsed = None

                if parsed and parsed.get('visitante'):
                    visitante = parsed['visitante']
                    visitante_id = visitante.get('id') or visitante.get('chave')
                    # Attempt to locate an Evento to register presence. Prefer a future or today's event in the same igreja
                    from eventos.models import Evento
                    evento = None
                    try:
                        # Prefer evento linked to request.igreja_ativa
                        if getattr(request, 'igreja_ativa', None):
                            evento = Evento.objects.filter(igreja=request.igreja_ativa).order_by('data_inicio').first()
                        if not evento:
                            evento = Evento.objects.first()
                    except Exception:
                        evento = None

                    if not evento:
                        self.stdout.write('NO_EVENT_FOUND_FOR_PRESENCE_TEST')
                    else:
                        # Build a POST request to ajax_registrar_presenca_evento
                        from secretaria.views import ajax_registrar_presenca_evento
                        rf2 = RequestFactory()
                        post_data = {'evento': str(evento.pk), 'membro': str(visitante_id)}
                        req2 = rf2.post('/sistema/visitantes/ajax-registrar-presenca/', data=post_data, **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
                        req2.user = user
                        try:
                            req2.igreja_ativa = request.igreja_ativa
                        except Exception:
                            pass
                        try:
                            resp2 = ajax_registrar_presenca_evento(req2)
                        except Exception as e:
                            self.stdout.write('PRESENCE VIEW RAISED EXCEPTION: %s' % e)
                            traceback.print_exc(file=self.stdout)
                            return

                        try:
                            status2 = getattr(resp2, 'status_code', 'N/A')
                            self.stdout.write('PRESENCE STATUS: %s' % status2)
                            content2 = getattr(resp2, 'content', b'').decode('utf-8')
                            try:
                                parsed2 = json.loads(content2)
                                self.stdout.write(json.dumps(parsed2, ensure_ascii=False, indent=2))
                            except Exception:
                                self.stdout.write('PRESENCE RAW RESPONSE:\n' + content2)
                        except Exception as e:
                            self.stdout.write('PRESENCE RESPONSE READ ERROR: %s' % e)
                            traceback.print_exc(file=self.stdout)
                else:
                    self.stdout.write('VISITANTE_NOT_RETURNED_BY_CREATE_VIEW')
            except Exception as e:
                self.stdout.write('PRESENCE TEST ERROR: %s' % e)
                traceback.print_exc(file=self.stdout)

            # If view returned an HttpResponse-like object, inspect it
            try:
                status = getattr(resp, 'status_code', 'N/A')
                self.stdout.write('STATUS: %s' % status)
                content = getattr(resp, 'content', b'').decode('utf-8')
                try:
                    parsed = json.loads(content)
                    self.stdout.write(json.dumps(parsed, ensure_ascii=False, indent=2))
                except Exception:
                    self.stdout.write('RAW RESPONSE:\n' + content)
            except Exception as e:
                self.stdout.write('RESPONSE READ ERROR: %s' % e)
                traceback.print_exc(file=self.stdout)
        except Exception as e:
            self.stdout.write('REQUEST FACTORY ERROR: %s' % e)
            traceback.print_exc(file=self.stdout)
